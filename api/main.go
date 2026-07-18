package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	awshttp "github.com/aws/aws-sdk-go-v2/aws/transport/http"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/labstack/echo/v4"
	"golang.org/x/net/http2"

	_ "github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	_config "github.com/USACE/cumulus-api/api/config"
	"github.com/USACE/cumulus-api/api/handlers"
	"github.com/USACE/cumulus-api/api/middleware"

	"github.com/labstack/echo-contrib/prometheus"
)

// Connection returns a database connection from configuration parameters
func Connection(cfg *_config.Config) *pgxpool.Pool {

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
	// set the application name in pg_stat_activity to identify the connection
	poolConfig.ConnConfig.RuntimeParams["application_name"] = "cumulus-api"

	db, err := pgxpool.NewWithConfig(context.Background(), poolConfig)
	if err != nil {
		log.Panic(err.Error())
	}

	return db
}

func main() {

	// Environment Variable Config
	cfg, err := _config.GetConfig()
	if err != nil {
		log.Fatal(err.Error())
	}
	// Download links are HMAC-signed; an empty key would make them forgeable.
	// GetConfig falls back to ApplicationKey when no dedicated secret is set, so
	// warn (to nudge setting a real one) but only fail if BOTH are empty.
	if os.Getenv("CUMULUS_DOWNLOAD_LINK_SECRET") == "" {
		log.Println("WARNING: CUMULUS_DOWNLOAD_LINK_SECRET not set; signing download links with APPLICATION_KEY as a temporary fallback. Configure a dedicated secret.")
	}
	if cfg.DownloadLinkSecret == "" {
		log.Fatal("neither CUMULUS_DOWNLOAD_LINK_SECRET nor CUMULUS_APPLICATION_KEY is set; cannot sign download links")
	}

	// AWS Config
	cfg.AwsConfig, err = config.LoadDefaultConfig(
		context.Background(),
		func(o *config.LoadOptions) error {
			o.Region = cfg.AWSS3Region
			return nil
		})

	// One shared S3 client for the COG proxy. SDK v2 already shares the credential provider + HTTP
	// client via the config, but building the client once (no per-request allocation) and widening
	// the idle-connection pool lets the high request concurrency of a COG import reuse keep-alive
	// connections to S3 instead of re-handshaking. Safe for concurrent use; credentials auto-refresh.
	cogHTTPClient := awshttp.NewBuildableClient().WithTransportOptions(func(t *http.Transport) {
		t.MaxIdleConns = 200
		t.MaxIdleConnsPerHost = 100
		t.IdleConnTimeout = 90 * time.Second
	})
	cogS3Client := s3.NewFromConfig(cfg.AwsConfig, func(o *s3.Options) {
		o.UsePathStyle = cfg.AWSS3ForcePathStyle
		o.HTTPClient = cogHTTPClient
	})

	// Database
	db := Connection(cfg)

	e := echo.New()
	// Middleware for All Routes
	e.Use(middleware.CORS, middleware.GZIP)

	// Middleware to serve static content from s3
	// Make sure it is last in the middleware chain
	e.Use(middleware.S3StaticWithConfig(middleware.S3StaticConfig{
		Bucket:      cfg.AWSS3Bucket,
		Prefix:      cfg.AWSS3BucketPrefix,
		Environment: cfg.AuthEnvironment,
		Endpoint:    cfg.AWSS3Endpoint,
		Skipper: func(c echo.Context) bool {
			return strings.HasPrefix(c.Request().URL.Path, "/api/") || strings.HasPrefix(c.Request().URL.Path, "/features/")
		},
	}))

	// API Routes
	api := e.Group("api")

	// Public Routes
	public := api.Group("")

	// Private Routes Supporting CAC (JWT) or Key Auth
	private := api.Group("")

	// JWT Authentication Middleware
	log.Printf("AUTH_ENVIRONMENT: %s", cfg.AuthEnvironment)
	switch strings.ToUpper(cfg.AuthEnvironment) {
	case "MOCK":
		private.Use(middleware.JWTMock)
	case "DEVELOP":
		private.Use(middleware.JWTDevelop)
	case "STABLE":
		private.Use(middleware.JWTStable)
	case "TEST":
		private.Use(middleware.JWTTest)
	case "PROD":
		private.Use(middleware.JWTProd)
	default:
		log.Fatalf("Unknown AUTH_ENVIRONMENT Variable: %s", cfg.AuthEnvironment)
	}

	// Key Authentication Middleware
	private.Use(middleware.KeyAuth(cfg.ApplicationKey), middleware.AttachUserInfo(db))

	// Health Check
	public.GET("/health", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]interface{}{
			"status":  "healthy",
			"version": "2.08.00",
		})
	})

	// Identity Provider Configuration Route
	public.GET("/identity-provider/configuration", func(c echo.Context) error {
		return handlers.GetIdentityProviderConfiguration(cfg.AuthEnvironment, c)
	})

	// Proxy to pg_featureserv
	features := e.Group("/features")
	features.Use(middleware.PgFeatureservProxy(cfg.PgFeatureservUrl))

	// Acquirables
	public.GET("/acquirables", handlers.ListAcquirables(db))
	private.GET("/acquirables/:acquirable_id/files", handlers.ListAcquirablefiles(db))
	private.POST("/acquirablefiles", handlers.CreateAcquirablefiles(db),
		middleware.IsAdmin,
	)

	// Offices
	public.GET("/offices", handlers.ListOffices(db))

	// Products
	public.GET("/product_ingest_status", handlers.GetProductIngestStatus(db))
	public.GET("/product_slugs", handlers.GetProductSlugs(db))
	public.GET("/products", handlers.ListProducts(db))
	public.GET("/products/:product_id/file-availability", handlers.GetProductFileAvailability(db))
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
	// Direct, Range-capable COG access (authenticated + metered) for desktop clients
	private.GET("/products/:product_id/cog-files", handlers.ListProductfilesCOG(db))
	private.GET("/products/:product_id/cog/:productfile_id", handlers.StreamProductfileCOG(db, cogS3Client))
	private.HEAD("/products/:product_id/cog/:productfile_id", handlers.StreamProductfileCOG(db, cogS3Client))

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

	// DSS Specific Information
	public.GET("/dss/datatypes", handlers.ListDssDatatypes(db))

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

	// Serve Downloads (signature-gated: see ServeDownloadFile, since the
	// frontend triggers this via window.open and can't attach a bearer JWT)
	public.GET("/downloads/:download_id/file", handlers.ServeDownloadFile(
		db, &cfg.AwsConfig, &cfg.AWSS3Bucket, cfg.AWSS3ForcePathStyle, cfg.DownloadLinkSecret,
	))

	// List Downloads
	private.GET("/downloads", handlers.ListAdminDownloads(db), middleware.IsAdmin)
	// Admin Usage Report
	private.GET("/downloads/usage", handlers.ListDownloadUsage(db), middleware.IsAdmin)
	private.GET("/downloads/usage/products", handlers.ListProductUsage(db), middleware.IsAdmin)
	// Admin Analytics (filtered totals/breakdowns, timeline, user selector)
	private.GET("/downloads/usage/summary", handlers.GetUsageSummary(db), middleware.IsAdmin)
	private.GET("/downloads/usage/timeseries", handlers.GetUsageTimeseries(db), middleware.IsAdmin)
	private.GET("/downloads/usage/users", handlers.ListUsageUsers(db), middleware.IsAdmin)
	// Create Download (Anonymous)
	public.POST("/deprecated/anonymous_downloads", handlers.CreateDownload(db, cfg), middleware.AttachAnonymousUserInfo) // deprecated
	private.POST("/downloads", handlers.CreateDownload(db, cfg))
	// Auth required: this returns a freshly-signed download link, so it must not
	// be reachable anonymously. Packager calls it with ?key=APPLICATION_KEY.
	private.GET("/downloads/:download_id", handlers.GetDownload(db))
	// Create Download (Authenticated)
	private.POST("/my_downloads", handlers.CreateDownload(db, cfg))
	private.GET("/my_downloads", handlers.ListMyDownloads(db))
	// Routes used by packager to prepare download
	public.GET("/downloads/:download_id/packager_request", handlers.GetDownloadPackagerRequest(db))
	private.PUT("/downloads/:download_id", handlers.UpdateDownload(db))

	// Metrics
	// -- Download Metrics
	public.GET("/metrics/downloads", handlers.GetDownloadMetrics(db))

	// User Regions
	private.GET("/user-regions", handlers.ListMyRegions(db))
	private.GET("/user-regions/public", handlers.ListPublicRegions(db))
	private.GET("/user-regions/search", handlers.SearchUserRegions(db))
	private.GET("/user-regions/:region_id", handlers.GetUserRegion(db))
	private.POST("/user-regions", handlers.CreateUserRegion(db))
	private.PUT("/user-regions/:region_id", handlers.UpdateUserRegion(db))
	private.DELETE("/user-regions/:region_id", handlers.DeleteUserRegion(db))

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
