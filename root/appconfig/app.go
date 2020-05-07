package appconfig

import (
	"log"

	"github.com/kelseyhightower/envconfig"
	"github.com/labstack/echo/middleware"
)

//
var appname string = "cumulus"

// Config holds all configuration variables for the application
type Config struct {
	DBUser        string
	DBPass        string
	DBName        string
	DBHost        string
	DBSSLMode     string
	JWTDisabled   bool
	JWTConfig     *middleware.JWTConfig
	LambdaContext bool
}

// AppConfig returns a populated application configuration struct
func AppConfig() *Config {
	// Get Config Parameters from Environment Variables
	var cfg Config
	err := envconfig.Process(appname, &cfg)
	if err != nil {
		log.Fatal(err.Error())
	}
	// Set JWT Configuration, pass it the config so far
	cfg.JWTConfig = JWTConfig(&cfg)

	return &cfg
}
