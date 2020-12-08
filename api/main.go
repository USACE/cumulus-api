package main

import (
	"api/models"
	"fmt"
	"log"
	"net/http"

	"api/config"
	"api/handlers"
	"api/middleware"

	"github.com/USACE/go-simple-asyncer/asyncer"
	"github.com/jmoiron/sqlx"

	"github.com/apex/gateway"
	"github.com/labstack/echo/v4"

	_ "github.com/lib/pq"
)

// Connection returns a database connection from configuration parameters
func Connection(cfg *config.Config) *sqlx.DB {
	connStr := func(cfg *config.Config) string {
		return fmt.Sprintf(
			"user=%s password=%s dbname=%s host=%s sslmode=%s binary_parameters=yes",
			cfg.DBUser, cfg.DBPass, cfg.DBName, cfg.DBHost, cfg.DBSSLMode,
		)
	}
	return sqlx.MustOpen("postgres", connStr(cfg))
}

func main() {
	//  Here's what would typically be here:
	// lambda.Start(Handler)
	//
	// There were a few options on how to incorporate Echo v4 on Lambda.
	//
	// Landed here for now:
	//
	//     https://github.com/apex/gateway
	//     https://github.com/labstack/echo/issues/1195
	//
	// With this for local development:
	//     https://medium.com/a-man-with-no-server/running-go-aws-lambdas-locally-with-sls-framework-and-sam-af3d648d49cb
	//
	// This looks promising and is from awslabs, but Echo v4 support isn't quite there yet.
	// There is a pull request in progress, Re-evaluate in April 2020.
	//
	//    https://github.com/awslabs/aws-lambda-go-api-proxy
	//

	// Environment Variable Config
	cfg, err := config.GetConfig()
	if err != nil {
		log.Fatal(err.Error())
	}

	// Database
	db := Connection(cfg)

	// packagerAsyncer defines async engine used to package DSS files for download
	packagerAsyncer, err := asyncer.NewAsyncer(
		asyncer.Config{Engine: cfg.AsyncEnginePackager, Target: cfg.AsyncEnginePackagerTarget},
	)
	if err != nil {
		log.Fatal(err.Error())
	}
	// acquisitionAsyncer defines async engine used to package DSS files for download
	acquisitionAsyncer, err := asyncer.NewAsyncer(
		asyncer.Config{Engine: cfg.AsyncEngineAcquisition, Target: cfg.AsyncEngineAcquisitionTarget},
	)
	if err != nil {
		log.Fatal(err.Error())
	}

	e := echo.New()
	// Middleware for All Routes
	e.Use(middleware.CORS, middleware.GZIP)

	// Public Routes
	public := e.Group("")

	/////////////////////////
	// Key or CAC Auth Routes
	/////////////////////////
	cacOrToken := e.Group("")
	if cfg.AuthJWTMocked {
		cacOrToken.Use(middleware.JWTMock(cfg.AuthDisabled, true))
	} else {
		cacOrToken.Use(middleware.JWT(cfg.AuthDisabled, true))
	}
	cacOrToken.Use(middleware.KeyAuth(
		cfg.AuthDisabled,
		cfg.ApplicationKey,
		func(keyID string) (string, error) {
			k, err := models.GetTokenInfoByTokenID(db, &keyID)
			if err != nil {
				return "", err
			}
			return k.Hash, nil
		}),
	)

	/////////////////////////////////////////
	// CAC Only Routes (API Keys Not Allowed)
	/////////////////////////////////////////
	cacOnly := e.Group("")
	if cfg.AuthJWTMocked {
		cacOnly.Use(middleware.JWTMock(cfg.AuthDisabled, false))
	} else {
		cacOnly.Use(middleware.JWT(cfg.AuthDisabled, false))
	}
	cacOnly.Use(middleware.IsLoggedIn)

	// Public Routes
	public.GET("cumulus/basins", handlers.ListBasins(db))
	public.GET("cumulus/:office_slug/basins", handlers.ListOfficeBasins(db))
	public.GET("cumulus/basins/:id", handlers.GetBasin(db))
	public.GET("cumulus/products", handlers.ListProducts(db))
	public.GET("cumulus/products/:id", handlers.GetProduct(db))
	public.GET("cumulus/products/:id/availability", handlers.GetProductAvailability(db))
	public.GET("cumulus/products/:id/files", handlers.GetProductProductfiles(db))
	public.GET("cumulus/acquirables", handlers.ListAcquirableInfo(db))

	// Downloads
	public.GET("cumulus/downloads", handlers.ListDownloads(db))
	public.GET("cumulus/downloads/:id", handlers.GetDownload(db))
	public.GET("cumulus/downloads/:id/packager_request", handlers.GetDownloadPackagerRequest(db))
	public.POST("cumulus/downloads", handlers.CreateDownload(db, packagerAsyncer))
	public.PUT("cumulus/downloads/:id", handlers.UpdateDownload(db))

	// Restricted Routes (JWT or Key)
	cacOrToken.POST("cumulus/acquire", handlers.DoAcquire(db, acquisitionAsyncer))
	cacOrToken.POST("cumulus/products/:id/acquire", handlers.CreateAcquisitionAttempt(db))

	// Basins
	cacOrToken.POST("cumulus/basins/:basin_id/products/:product_id/statistics/enable", handlers.EnableBasinProductStatistics(db))
	cacOrToken.POST("cumulus/basins/:basin_id/products/:product_id/statistics/disable", handlers.DisableBasinProductStatistics(db))

	// Watersheds (to replace basins)
	public.GET("cumulus/watersheds", handlers.ListWatersheds(db))
	public.GET("cumulus/watersheds/:watershed_id", handlers.GetWatershed(db))
	cacOrToken.POST("cumulus/watersheds", handlers.CreateWatershed(db))
	cacOrToken.PUT("cumulus/watersheds/:watershed_id", handlers.UpdateWatershed(db))
	cacOrToken.DELETE("cumulus/watersheds/:watershed_id", handlers.DeleteWatershed(db))

	// JWT Only Restricted Routes (JWT Only)
	cacOnly.POST("cumulus/profiles", handlers.CreateProfile(db))
	cacOnly.GET("cumulus/my_profile", handlers.GetMyProfile(db))
	cacOnly.POST("cumulus/my_tokens", handlers.CreateToken(db))
	cacOnly.DELETE("cumulus/my_tokens/:token_id", handlers.DeleteToken(db))

	// Start server
	lambda := cfg.LambdaContext
	log.Printf("starting server; Running On AWS LAMBDA: %t", lambda)
	if lambda {
		log.Fatal(gateway.ListenAndServe("localhost:3030", e))
	} else {
		log.Fatal(http.ListenAndServe(":3030", e))
	}
}
