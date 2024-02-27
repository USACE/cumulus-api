package main

import (
	"fmt"
	"net/http"
	"os"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	// Create an Echo instance
	e := echo.New()

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	// Public Health Check Route
	e.GET("/health", func(c echo.Context) error {
		return c.JSON(http.StatusOK, map[string]interface{}{"status": "healthy"})
	})

	// Serve static files from the "static" directory

	e.Use(middleware.StaticWithConfig(middleware.StaticConfig{
		Root:   "data",
		Browse: false,
		HTML5:  true,
		Index:  "index.html",
	}))

	// Get the port from the PORT environment variable, default to 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Start the server
	address := fmt.Sprintf(":%s", port)
	e.Logger.Fatal(e.Start(address))
}
