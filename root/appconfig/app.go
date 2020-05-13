package appconfig

import (
	"api/root/asyncer"
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
	AsyncEngine     string
	Asyncer         asyncer.Asyncer
}

// SetAsyncer sets the asyncer
func SetAsyncer(cfg *Config) error {
	switch cfg.AsyncEngine {
	case "AWSLAMBDA":
		cfg.Asyncer = asyncer.LambdaAsyncer{}
	default:
		cfg.Asyncer = asyncer.MockAsyncer{}
	}
	return nil
}

// GetConfig returns a populated application configuration struct
func GetConfig() *Config {
	// Get Config Parameters from Environment Variables
	var cfg Config
	err := envconfig.Process(appname, &cfg)
	if err != nil {
		log.Fatal(err.Error())
	}
	// Set Asyncer
	SetAsyncer(&cfg)

	return &cfg
}
