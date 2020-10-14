package main

import (
	"api/root/models"
	"fmt"
	"log"
	"net/http"

	"api/root/handlers"
	"api/root/middleware"

	"github.com/USACE/go-simple-asyncer/asyncer"

	"github.com/apex/gateway"
	"github.com/kelseyhightower/envconfig"
	"github.com/labstack/echo"

	"github.com/jmoiron/sqlx"

	_ "github.com/lib/pq"
)

// Config holds application configuration variables
type Config struct {
	DBUser                         string
	DBPass                         string
	DBName                         string
	DBHost                         string
	DBSSLMode                      string
	AuthDisabled                   bool `split_words:"true"`
	LambdaContext                  bool
	AsyncEngineAcquisition         string `envconfig:"ASYNC_ENGINE_ACQUISITION"`
	AsyncEngineAcquisitionSNSTopic string `envconfig:"ASYNC_ENGINE_ACQUISITION_SNS_TOPIC"`
	AsyncEnginePackager            string `envconfig:"ASYNC_ENGINE_PACKAGER"`
	AsyncEnginePackagerSNSTopic    string `envconfig:"ASYNC_ENGINE_PACKAGER_SNS_TOPIC"`
}

// Connection returns a database connection from configuration parameters
func Connection(cfg *Config) *sqlx.DB {
	connStr := func(cfg *Config) string {
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
	var cfg Config
	if err := envconfig.Process("cumulus", &cfg); err != nil {
		log.Fatal(err.Error())
	}

	// Database
	db := Connection(&cfg)

	// packagerAsyncer defines async engine used to package DSS files for download
	packagerAsyncer, err := asyncer.NewAsyncer(
		asyncer.Config{Engine: cfg.AsyncEnginePackager, Topic: cfg.AsyncEnginePackagerSNSTopic},
	)
	if err != nil {
		log.Fatal(err.Error())
	}
	// acquisitionAsyncer defines async engine used to package DSS files for download
	acquisitionAsyncer, err := asyncer.NewAsyncer(
		asyncer.Config{Engine: cfg.AsyncEngineAcquisition, Topic: cfg.AsyncEngineAcquisitionSNSTopic},
	)
	if err != nil {
		log.Fatal(err.Error())
	}

	e := echo.New()
	// Middleware for All Routes
	e.Use(middleware.CORS, middleware.GZIP)

	// Public Routes
	public := e.Group("")
	// Key or CAC Auth Routes
	cacOrToken := e.Group("")
	cacOrToken.Use(
		middleware.JWT(cfg.AuthDisabled, true),
		middleware.KeyAuth(cfg.AuthDisabled, models.MustListKeyInfo(db)),
	)
	// CAC Only Routes (API Keys Not Allowed)
	cacOnly := e.Group("")
	cacOnly.Use(
		middleware.JWT(cfg.AuthDisabled, false),
	)

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
	public.POST("cumulus/downloads", handlers.CreateDownload(db, packagerAsyncer))
	public.PUT("cumulus/downloads/:id", handlers.UpdateDownload(db))

	// Restricted Routes (JWT or Key)
	cacOrToken.POST("cumulus/acquire", handlers.DoAcquire(db, acquisitionAsyncer))
	cacOrToken.POST("cumulus/products/:id/acquire", handlers.CreateAcquisitionAttempt(db))

	// JWT Only Restricted Routes (JWT Only)
	cacOnly.POST("cumulus/keys", handlers.CreateKey(db))

	// Start server
	lambda := cfg.LambdaContext
	log.Printf("starting server; Running On AWS LAMBDA: %t", lambda)
	if lambda {
		log.Fatal(gateway.ListenAndServe("localhost:3030", e))
	} else {
		log.Fatal(http.ListenAndServe("localhost:3030", e))
	}
}
