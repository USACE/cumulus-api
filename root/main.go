package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"

	"api/root/handlers"

	"github.com/apex/gateway"
	"github.com/labstack/echo"

	_ "github.com/lib/pq"
)

func lambdaContext() bool {

	value, exists := os.LookupEnv("LAMBDA")

	if exists && strings.ToUpper(value) == "TRUE" {
		return true
	}
	return false
}

func dbConnStr() string {

	log.Printf("get database connection string")

	dbuser := os.Getenv("DB_USER")
	dbpass := os.Getenv("DB_PASS")
	dbname := os.Getenv("DB_NAME")
	dbhost := os.Getenv("DB_HOST")
	sslmode := os.Getenv("DB_SSLMODE")

	return fmt.Sprintf(
		"user=%s password=%s dbname=%s host=%s sslmode=%s",
		dbuser, dbpass, dbname, dbhost, sslmode,
	)
}

func initDB(connStr string) *sql.DB {

	log.Printf("Getting database connection")
	db, err := sql.Open("postgres", connStr)

	if err != nil {
		panic(err)
	}

	if db == nil {
		log.Panicf("database is nil")
	}

	return db
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

	db := initDB(dbConnStr())

	e := echo.New()
	// e.Pre(middleware.RemoveTrailingSlash())

	// Routes
	e.GET("cumulus/test", handlers.GetTest)
	e.GET("cumulus/basins", handlers.ListBasins(db))
	e.GET("cumulus/basins/:id", handlers.GetBasin(db))
	e.GET("cumulus/products", handlers.ListProducts(db))
	e.GET("cumulus/products/:id", handlers.GetProduct(db))
	e.GET("cumulus/products/:id/files", handlers.GetProductProductfiles(db))

	log.Printf(
		"starting server; Running On AWS LAMBDA: %t",
		lambdaContext(),
	)

	if lambdaContext() {
		log.Fatal(gateway.ListenAndServe(":3000", e))
	} else {
		log.Fatal(http.ListenAndServe(":3000", e))
	}
}
