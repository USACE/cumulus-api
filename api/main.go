package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
	"golang.org/x/net/http2"

	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"

	"github.com/USACE/cumulus-api/api/config"
	"github.com/USACE/cumulus-api/api/handlers"
	"github.com/USACE/cumulus-api/api/middleware"

	"github.com/labstack/echo-contrib/prometheus"
)

// Connection returns a database connection from configuration parameters
func Connection(cfg *config.Config) *pgxpool.Pool {

	poolConfig, err := pgxpool.ParseConfig(
		fmt.Sprintf(
			"user=%s password=%s dbname=%s host=%s sslmode=%s",
			cfg.DBUser, cfg.DBPass, cfg.DBName, cfg.DBHost, cfg.DBSSLMode,
		),
	)
	if err != nil {
		log.Panic(err.Error())
	}
	poolConfig.MaxConns = 15
	poolConfig.MaxConnIdleTime = time.Minute * 30
	poolConfig.MinConns = 10

	db, err := pgxpool.ConnectConfig(context.Background(), poolConfig)
	if err != nil {
		log.Panic(err.Error())
	}

	return db
}

func main() {

	// Environment Variable Config
	cfg, err := config.GetConfig()
	if err != nil {
		log.Fatal(err.Error())
	}

	// AWS Config
	awsCfg := cfg.AWSConfig()

	// Database
	db := Connection(cfg)

	e := echo.New()
	// Middleware for All Routes
	e.Use(middleware.CORS, middleware.GZIP)

	// Public Routes
	public := e.Group("")

	// Private Routes Supporting CAC (JWT) or Key Auth
	private := e.Group("")

	// JWT Authentication Middleware
	log.Printf("AUTH_ENVIRONMENT: %s", cfg.AuthEnvironment)
	switch strings.ToUpper(cfg.AuthEnvironment) {
	case "MOCK":
		private.Use(middleware.JWTMock)
	case "DEVELOP":
		private.Use(middleware.JWTDevelop)
	case "STABLE":
		private.Use(middleware.JWTStable)
	default:
		log.Fatalf("Unknown AUTH_ENVIRONMENT Variable: %s", cfg.AuthEnvironment)
	}

	// Key Authentication Middleware
	private.Use(middleware.KeyAuth(cfg.ApplicationKey), middleware.AttachUserInfo)

	// Health Check
	public.GET("/health", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]interface{}{"status": "healthy"})
	})

	// Proxy to pg_featureserv
	features := public.Group("/features")
	features.Use(middleware.PgFeatureservProxy(cfg.PgFeatureservUrl))

	// Acquirables
	public.GET("/acquirables", handlers.ListAcquirables(db))
	private.GET("/acquirables/:acquirable_id/files", handlers.ListAcquirablefiles(db))
	private.POST("/acquirablefiles", handlers.CreateAcquirablefiles(db),
		middleware.IsAdmin,
	)

	// Products
	public.GET("/product_slugs", handlers.GetProductSlugs(db))
	public.GET("/products", handlers.ListProducts(db))
	public.GET("/products/:product_id", handlers.GetProduct(db))
	private.POST("/products", handlers.CreateProduct(db),
		middleware.IsAdmin,
	)
	private.PUT("/products/:product_id", handlers.UpdateProduct(db),
		middleware.IsAdmin,
	)
	private.DELETE("/products/:product_id", handlers.DeleteProduct(db),
		middleware.IsAdmin,
	)
	private.POST("/products/:product_id/undelete", handlers.UndeleteProduct(db),
		middleware.IsAdmin,
	)
	// Additional Information About Products
	public.GET("/products/:product_id/availability", handlers.GetProductAvailability(db))
	public.GET("/products/:product_id/files", handlers.ListProductfiles(db))

	// Productfiles
	private.POST("/productfiles", handlers.CreateProductfiles(db),
		middleware.IsAdmin,
	)

	// Suites
	public.GET("/suites", handlers.ListSuites(db))
	public.GET("/suites/:suite_id", handlers.GetSuite(db))
	private.POST("/suites", handlers.CreateSuite(db),
		middleware.IsAdmin,
	)
	private.PUT("/suites/:suite_id", handlers.UpdateSuite(db),
		middleware.IsAdmin,
	)
	private.DELETE("/suites/:suite_id", handlers.DeleteSuite(db),
		middleware.IsAdmin,
	)

	// Tags
	public.GET("/tags", handlers.ListTags(db))
	public.GET("/tags/:tag_id", handlers.GetTag(db))
	private.POST("/tags", handlers.CreateTag(db),
		middleware.IsAdmin,
	)
	private.PUT("/tags/:tag_id", handlers.UpdateTag(db),
		middleware.IsAdmin,
	)
	private.DELETE("/tags/:tag_id", handlers.DeleteTag(db),
		middleware.IsAdmin,
	)
	// Tag or Untag Product
	private.POST("/products/:product_id/tags/:tag_id", handlers.TagProduct(db),
		middleware.IsAdmin,
	)
	private.DELETE("/products/:product_id/tags/:tag_id", handlers.UntagProduct(db),
		middleware.IsAdmin,
	)

	// Units
	public.GET("/units", handlers.ListUnits(db))
	public.GET("/units/:unit_id", handlers.GetUnit(db))
	private.POST("/units", handlers.CreateUnit(db),
		middleware.IsAdmin,
	)
	private.PUT("/units/:unit_id", handlers.UpdateUnit(db),
		middleware.IsAdmin,
	)
	private.DELETE("/units/:unit_id", handlers.DeleteUnit(db),
		middleware.IsAdmin,
	)

	// Parameters
	public.GET("/parameters", handlers.ListParameters(db))
	public.GET("/parameters/:parameter_id", handlers.GetParameter(db))
	private.POST("/parameters", handlers.CreateParameter(db),
		middleware.IsAdmin,
	)
	private.PUT("/parameters/:parameter_id", handlers.UpdateParameter(db),
		middleware.IsAdmin,
	)
	private.DELETE("/parameters/:parameter_id", handlers.DeleteParameter(db),
		middleware.IsAdmin,
	)

	// Downloads
	public.GET("/cumulus/download/*", handlers.ServeMedia(&awsCfg, &cfg.AWSS3Bucket)) // Serve Downloads
	// List Downloads
	private.GET("/downloads", handlers.ListAdminDownloads(db), middleware.IsAdmin)
	// Create Download (Anonymous)
	public.POST("/deprecated/anonymous_downloads", handlers.CreateDownload(db, cfg), middleware.AttachAnonymousUserInfo) // deprecated
	private.POST("/downloads", handlers.CreateDownload(db, cfg))
	public.GET("/downloads/:download_id", handlers.GetDownload(db))
	// Create Download (Authenticated)
	private.POST("/my_downloads", handlers.CreateDownload(db, cfg))
	private.GET("/my_downloads", handlers.ListMyDownloads(db))
	// Routes used by packager to prepare download
	public.GET("/downloads/:download_id/packager_request", handlers.GetDownloadPackagerRequest(db))
	private.PUT("/downloads/:download_id", handlers.UpdateDownload(db))

	// Metrics
	// -- Download Metrics
	public.GET("/metrics/downloads", handlers.GetDownloadMetrics(db))

	// // Watersheds
	public.GET("/watersheds", handlers.ListWatersheds(db))
	public.GET("/watersheds/:watershed_id", handlers.GetWatershed(db))
	private.POST("/watersheds", handlers.CreateWatershed(db),
		middleware.IsAdmin,
	)
	private.PUT("/watersheds/:watershed_id", handlers.UpdateWatershed(db),
		middleware.IsAdmin,
	)
	private.DELETE("/watersheds/:watershed_id", handlers.DeleteWatershed(db),
		middleware.IsAdmin,
	)
	private.POST("/watersheds/:watershed_id/undelete", handlers.UndeleteWatershed(db),
		middleware.IsAdmin,
	)

	// My Watersheds
	private.GET("/my_watersheds", handlers.ListMyWatersheds(db))
	private.POST("/my_watersheds/:watershed_id", handlers.MyWatershedsAdd(db))
	private.DELETE("/my_watersheds/:watershed_id", handlers.MyWatershedsRemove(db))

	// // Area Groups
	// // TODO: CRUD Handlers for area_groups
	// public.GET("/watersheds/:watershed_id/area_groups", handlers.ListWatershedAreaGroups(db))
	public.GET("/watersheds/:watershed_id/area_groups/:area_group_id/areas", handlers.ListAreaGroupAreas(db))
	// // private.POST("watersheds/:watershed_id/area_groups", handlers.CreateAreaGroup(db))
	// // private.PUT("watersheds/:watershed_id/area_groups/:area_group_id", handlers.UpdateAreaGroup(db))
	// // private.DELETE("watersheds/:watershed_id/area_groups/:area_group_id", handlers.DeleteAreaGroup(db))
	// private.POST("/watersheds/:watershed_id/area_groups/:area_group_id/products/:product_id/statistics/enable", handlers.EnableAreaGroupProductStatistics(db))
	// private.POST("/watersheds/:watershed_id/area_groups/:area_group_id/products/:product_id/statistics/disable", handlers.DisableAreaGroupProductStatistics(db))

	// Create Prometheus server and Middleware
	eProm := echo.New()
	eProm.HideBanner = true
	prom := prometheus.NewPrometheus("cumulus_api", middleware.MetricsUrlSkipper)

	// Scrape metrics from Main Server
	e.Use(prom.HandlerFunc)
	// Setup metrics endpoint at another server
	prom.SetMetricsPath(eProm)

	go func() { eProm.Logger.Fatal(eProm.Start(":9090")) }()

	// Start main API server
	s := &http2.Server{
		MaxConcurrentStreams: 250,     // http2 default 250
		MaxReadFrameSize:     1048576, // http2 default 1048576
		IdleTimeout:          10 * time.Second,
	}
	if err := e.StartH2CServer(":80", s); err != http.ErrServerClosed {
		log.Fatal(err)
	}
}
