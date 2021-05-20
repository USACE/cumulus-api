package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"time"

	"api/config"
	"api/handlers"
	"api/middleware"
	"api/models"

	"github.com/labstack/echo/v4"

	_ "github.com/jackc/pgx/v4"
	"github.com/jackc/pgx/v4/pgxpool"
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
	// awsCfg := cfg.AWSConfig()

	// Database
	db := Connection(cfg)

	e := echo.New()
	// Middleware for All Routes
	e.Use(middleware.CORS, middleware.GZIP)

	// Public Routes
	public := e.Group("")

	// Private Routes Supporting CAC (JWT) or Key Auth
	private := e.Group("")
	// JWT (CAC) Middleware
	if cfg.AuthJWTMocked {
		private.Use(middleware.JWTMock(cfg.AuthDisabled, true))
	} else {
		private.Use(middleware.JWT(cfg.AuthDisabled, true))
	}
	// Key Auth Middleware
	private.Use(middleware.KeyAuth(
		cfg.AuthDisabled,
		cfg.ApplicationKey,
		func(keyID string) (string, error) {
			k, err := models.GetTokenInfoByTokenID(db, &keyID)
			if err != nil {
				return "", err
			}
			return k.Hash, nil
		},
	))

	/////////////////////////////////////////
	// CAC Only Routes (API Keys Not Allowed)
	/////////////////////////////////////////
	cacOnly := e.Group("")
	if cfg.AuthJWTMocked {
		cacOnly.Use(middleware.JWTMock(cfg.AuthDisabled, false))
	} else {
		cacOnly.Use(middleware.JWT(cfg.AuthDisabled, false))
	}
	// AttachProfileMiddleware attaches ProfileID to context, whether
	// authenticated by token or api key
	private.Use(middleware.EDIPIMiddleware, middleware.AttachProfileMiddleware(db))
	cacOnly.Use(middleware.EDIPIMiddleware, middleware.CACOnlyMiddleware)

	// Profile
	private.GET("/my_profile", handlers.GetMyProfile(db))
	cacOnly.POST("/my_profile", handlers.CreateProfile(db))

	// API Tokens
	cacOnly.POST("/my_tokens", handlers.CreateToken(db))
	private.DELETE("/my_tokens/:token_id", handlers.DeleteToken(db))

	// Products
	private.POST("/products", handlers.CreateProduct(db))
	public.GET("/products", handlers.ListProducts(db))
	public.GET("/products/:product_id", handlers.GetProduct(db))
	private.PUT("/products/:product_id", handlers.UpdateProduct(db))
	private.DELETE("/products/:product_id", handlers.DeleteProduct(db))
	private.POST("/products/:product_id/undelete", handlers.UndeleteProduct(db))
	// Additional Information About Products
	public.GET("/products/:product_id/availability", handlers.GetProductAvailability(db))
	public.GET("/products/:product_id/files", handlers.ListProductfiles(db))

	// Tags
	private.POST("/tags", handlers.CreateTag(db))
	public.GET("/tags", handlers.ListTags(db))
	public.GET("/tags/:tag_id", handlers.GetTag(db))
	private.PUT("/tags/:tag_id", handlers.UpdateTag(db))
	private.DELETE("/tags/:tag_id", handlers.DeleteTag(db))
	// Tag or Untag Product
	private.POST("/products/:product_id/tags/:tag_id", handlers.TagProduct(db))
	private.DELETE("/products/:product_id/tags/:tag_id", handlers.UntagProduct(db))

	// public.GET("/acquirables", handlers.ListAcquirables(db))

	// // Acquirables/Acquirablefiles
	// public.GET("/acquirables/:acquirable_id/files", handlers.ListAcquirablefiles(db))
	// cacOrToken.POST("/acquirablefiles", handlers.CreateAcquirablefiles(db))

	// // Downloads
	// public.GET("/downloads", handlers.ListDownloads(db))
	// cacOnly.GET("/my_downloads", handlers.ListMyDownloads(db))
	// cacOnly.POST("/my_downloads", handlers.CreateDownload(db))
	// public.GET("/downloads/:id", handlers.GetDownload(db))
	// public.GET("/downloads/:id/packager_request", handlers.GetDownloadPackagerRequest(db))
	// public.POST("/downloads", handlers.CreateDownload(db))
	// public.PUT("/downloads/:id", handlers.UpdateDownload(db))
	// // Serve Download Files
	// public.GET("/cumulus/download/dss/*", handlers.ServeMedia(&awsCfg, &cfg.AWSS3Bucket))

	// // Restricted Routes (JWT or Key)

	// // Watersheds
	// public.GET("/watersheds", handlers.ListWatersheds(db))
	// public.GET("/watersheds/:watershed_id", handlers.GetWatershed(db))
	// cacOrToken.POST("/watersheds", handlers.CreateWatershed(db))
	// cacOrToken.PUT("/watersheds/:watershed_id", handlers.UpdateWatershed(db))
	// cacOrToken.DELETE("/watersheds/:watershed_id", handlers.DeleteWatershed(db))

	// // My Watersheds
	// cacOnly.GET("/my_watersheds", handlers.ListMyWatersheds(db))
	// cacOnly.POST("/my_watersheds/:watershed_id/add", handlers.MyWatershedsAdd(db))
	// cacOnly.POST("/my_watersheds/:watershed_id/remove", handlers.MyWatershedsRemove(db))

	// // Area Groups
	// // TODO: CRUD Handlers for area_groups
	// public.GET("/watersheds/:watershed_id/area_groups", handlers.ListWatershedAreaGroups(db))
	// public.GET("/watersheds/:watershed_id/area_groups/:area_group_id/areas", handlers.ListAreaGroupAreas(db))
	// // cacOrToken.POST("watersheds/:watershed_id/area_groups", handlers.CreateAreaGroup(db))
	// // cacOrToken.PUT("watersheds/:watershed_id/area_groups/:area_group_id", handlers.UpdateAreaGroup(db))
	// // cacOrToken.DELETE("watersheds/:watershed_id/area_groups/:area_group_id", handlers.DeleteAreaGroup(db))
	// cacOrToken.POST("/watersheds/:watershed_id/area_groups/:area_group_id/products/:product_id/statistics/enable", handlers.EnableAreaGroupProductStatistics(db))
	// cacOrToken.POST("/watersheds/:watershed_id/area_groups/:area_group_id/products/:product_id/statistics/disable", handlers.DisableAreaGroupProductStatistics(db))

	// Start server
	log.Fatal(http.ListenAndServe(":80", e))
}
