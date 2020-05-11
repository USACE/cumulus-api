package appconfig

import (
	"log"

	"github.com/kelseyhightower/envconfig"
)

//
var appname string = "cumulus"

// Config holds all configuration variables for the application
type Config struct {
	DBUser          string
	DBPass          string
	DBName          string
	DBHost          string
	DBSSLMode       string
	JWTAuthDisabled bool
	KeyAuthDisabled bool
	LambdaContext   bool
}

// AppConfig returns a populated application configuration struct
func AppConfig() *Config {
	// Get Config Parameters from Environment Variables
	var cfg Config
	err := envconfig.Process(appname, &cfg)
	if err != nil {
		log.Fatal(err.Error())
	}

	return &cfg
}
