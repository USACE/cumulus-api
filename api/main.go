package main

import (
	"api/models"
	"fmt"
	"log"
	"net/http"

	"api/config"
	"api/handlers"
	"api/middleware"

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

	// AWS Config
	awsCfg := cfg.AWSConfig()

	// Database
	db := Connection(cfg)

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
	public.GET("/products", handlers.ListProducts(db))
	public.GET("/products/:id", handlers.GetProduct(db))
	public.GET("/products/:id/availability", handlers.GetProductAvailability(db))
	public.GET("/products/:id/files", handlers.GetProductProductfiles(db))
	public.GET("/acquirables", handlers.ListAcquirables(db))

	// Acquirables/Acquirablefiles
	public.GET("/acquirables/:acquirable_id/files", handlers.ListAcquirablefiles(db))
	cacOrToken.POST("/acquirablefiles", handlers.CreateAcquirablefiles(db))

	// Downloads
	public.GET("/downloads", handlers.ListDownloads(db))
	cacOnly.GET("/my_downloads", handlers.ListMyDownloads(db))
	cacOnly.POST("/my_downloads", handlers.CreateDownload(db))
	public.GET("/downloads/:id", handlers.GetDownload(db))
	public.GET("/downloads/:id/packager_request", handlers.GetDownloadPackagerRequest(db))
	public.POST("/downloads", handlers.CreateDownload(db))
	public.PUT("/downloads/:id", handlers.UpdateDownload(db))
	// Serve Download Files
	public.GET("/cumulus/download/dss/*", handlers.ServeMedia(&awsCfg, &cfg.AWSS3Bucket))

	// Restricted Routes (JWT or Key)

	// Watersheds
	public.GET("/watersheds", handlers.ListWatersheds(db))
	public.GET("/watersheds/:watershed_id", handlers.GetWatershed(db))
	cacOrToken.POST("/watersheds", handlers.CreateWatershed(db))
	cacOrToken.PUT("/watersheds/:watershed_id", handlers.UpdateWatershed(db))
	cacOrToken.DELETE("/watersheds/:watershed_id", handlers.DeleteWatershed(db))

	// My Watersheds
	cacOnly.GET("/my_watersheds", handlers.ListMyWatersheds(db))
	cacOnly.POST("/my_watersheds/:watershed_id/add", handlers.MyWatershedsAdd(db))
	cacOnly.POST("/my_watersheds/:watershed_id/remove", handlers.MyWatershedsRemove(db))

	// Area Groups
	// TODO: CRUD Handlers for area_groups
	public.GET("/watersheds/:watershed_id/area_groups", handlers.ListWatershedAreaGroups(db))
	public.GET("/watersheds/:watershed_id/area_groups/:area_group_id/areas", handlers.ListAreaGroupAreas(db))
	// cacOrToken.POST("watersheds/:watershed_id/area_groups", handlers.CreateAreaGroup(db))
	// cacOrToken.PUT("watersheds/:watershed_id/area_groups/:area_group_id", handlers.UpdateAreaGroup(db))
	// cacOrToken.DELETE("watersheds/:watershed_id/area_groups/:area_group_id", handlers.DeleteAreaGroup(db))
	cacOrToken.POST("/watersheds/:watershed_id/area_groups/:area_group_id/products/:product_id/statistics/enable", handlers.EnableAreaGroupProductStatistics(db))
	cacOrToken.POST("/watersheds/:watershed_id/area_groups/:area_group_id/products/:product_id/statistics/disable", handlers.DisableAreaGroupProductStatistics(db))

	// JWT Only Restricted Routes (JWT Only)
	cacOnly.POST("/profiles", handlers.CreateProfile(db))
	cacOnly.GET("/my_profile", handlers.GetMyProfile(db))
	cacOnly.POST("/my_tokens", handlers.CreateToken(db))
	cacOnly.DELETE("/my_tokens/:token_id", handlers.DeleteToken(db))

	// Start server
	lambda := cfg.LambdaContext
	log.Printf("starting server; Running On AWS LAMBDA: %t", lambda)
	if lambda {
		log.Fatal(gateway.ListenAndServe("localhost:3030", e))
	} else {
		log.Fatal(http.ListenAndServe(":80", e))
	}
}
