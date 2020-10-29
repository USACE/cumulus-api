package config

import (
	"log"

	"github.com/kelseyhightower/envconfig"
)

// Config holds application configuration variables
type Config struct {
	DBUser                       string
	DBPass                       string
	DBName                       string
	DBHost                       string
	DBSSLMode                    string
	AuthDisabled                 bool `split_words:"true"`
	AuthJWTMocked                bool `envconfig:"CUMULUS_AUTH_JWT_MOCKED"`
	LambdaContext                bool
	AsyncEngineAcquisition       string `envconfig:"ASYNC_ENGINE_ACQUISITION"`
	AsyncEngineAcquisitionTarget string `envconfig:"ASYNC_ENGINE_ACQUISITION_TARGET"`
	AsyncEnginePackager          string `envconfig:"ASYNC_ENGINE_PACKAGER"`
	AsyncEnginePackagerTarget    string `envconfig:"ASYNC_ENGINE_PACKAGER_TARGET"`
	StaticHost                   string `envconfig:"STATIC_HOST"`
	ApplicationKey               string `envconfig:"APPLICATION_KEY"`
}

// GetConfig returns environment variable config
func GetConfig() (*Config, error) {
	var cfg Config
	if err := envconfig.Process("cumulus", &cfg); err != nil {
		log.Fatal(err.Error())
	}
	return &cfg, nil
}

// StaticHost returns the static host
func StaticHost() (*string, error) {
	cfg, err := GetConfig()
	if err != nil {
		return nil, err
	}
	return &cfg.StaticHost, nil
}
