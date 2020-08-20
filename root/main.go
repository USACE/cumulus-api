package main

import (
	"log"
	"net/http"

	"api/root/appconfig"
	"api/root/handlers"

	"github.com/apex/gateway"
	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"

	_ "github.com/lib/pq"
)

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
	cfg := appconfig.GetConfig()

	db := appconfig.Connection(cfg)
	asyncer := cfg.Asyncer

	e := echo.New()

	// Middleware for All Routes
	e.Use(
		middleware.CORS(),
		middleware.GzipWithConfig(middleware.GzipConfig{Level: 5}),
	)

	// Public Routes
	public := e.Group("")
	// Allow Key or CAC Auth
	cacOrToken := e.Group("")
	cacOrToken.Use(middleware.KeyAuthWithConfig(*appconfig.KeyAuthConfig(cfg)))
	cacOrToken.Use(middleware.JWTWithConfig(*appconfig.JWTConfig(cfg, true)))
	// Allow CAC Auth Only (API Keys Not Allowed)
	cacOnly := e.Group("")
	cacOnly.Use(middleware.JWTWithConfig(*appconfig.JWTConfig(cfg, false)))

	// Public Routes
	public.GET("cumulus/basins", handlers.ListBasins(db))
	public.GET("cumulus/:office_slug/basins", handlers.ListOfficeBasins(db))
	public.GET("cumulus/basins/:id", handlers.GetBasin(db))
	public.GET("cumulus/products", handlers.ListProducts(db))
	public.GET("cumulus/products/:id", handlers.GetProduct(db))
	public.GET("cumulus/products/:id/availability", handlers.GetProductAvailability(db))
	public.GET("cumulus/products/:id/files", handlers.GetProductProductfiles(db))
	public.GET("cumulus/acquirables", handlers.ListAcquirables(db))
	// Downloads
	public.GET("cumulus/downloads", handlers.ListDownloads(db))
	public.GET("cumulus/downloads/:id", handlers.GetDownload(db))
	public.POST("cumulus/downloads", handlers.CreateDownload(db))
	public.POST("cumulus/downloads/:id", handlers.UpdateDownload(db))

	// Restricted Routes (JWT or Key)
	cacOrToken.POST("cumulus/acquire", handlers.DoAcquire(db, asyncer))
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
