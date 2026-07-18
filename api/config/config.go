package config

import (
	"log"

	"github.com/aws/aws-sdk-go-v2/aws"

	"github.com/kelseyhightower/envconfig"
)

// Config holds application configuration variables
type Config struct {
	AwsConfig                    aws.Config
	DBUser                       string
	DBPass                       string
	DBName                       string
	DBHost                       string
	DBSSLMode                    string
	AuthEnvironment              string `envconfig:"AUTH_ENVIRONMENT" default:"DEVELOP"`
	DownloadDefaultFormat        string `envconfig:"DOWNLOAD_DEFAULT_FORMAT" default:"dss7"`
	AsyncEngineAcquisition       string `envconfig:"ASYNC_ENGINE_ACQUISITION"`
	AsyncEngineAcquisitionTarget string `envconfig:"ASYNC_ENGINE_ACQUISITION_TARGET"`
	AsyncEnginePackager          string `envconfig:"ASYNC_ENGINE_PACKAGER"`
	AsyncEnginePackagerTarget    string `envconfig:"ASYNC_ENGINE_PACKAGER_TARGET"`
	AsyncEngineStatistics        string `envconfig:"ASYNC_ENGINE_STATISTICS"`
	AsyncEngineStatisticsTarget  string `envconfig:"ASYNC_ENGINE_STATISTICS_TARGET"`
	StaticHost                   string `envconfig:"STATIC_HOST"`
	ApplicationKey               string `envconfig:"APPLICATION_KEY"`
	DownloadLinkSecret           string `envconfig:"DOWNLOAD_LINK_SECRET"`
	AWSS3Endpoint                string `envconfig:"AWS_S3_ENDPOINT"`
	AWSS3Region                  string `envconfig:"AWS_S3_REGION"`
	AWSS3DisableSSL              bool   `envconfig:"AWS_S3_DISABLE_SSL"`
	AWSS3ForcePathStyle          bool   `envconfig:"AWS_S3_FORCE_PATH_STYLE"`
	AWSS3Bucket                  string `envconfig:"AWS_S3_BUCKET"`
	AWSS3BucketPrefix            string `envconfig:"AWS_S3_BUCKET_PREFIX"`
	PgFeatureservUrl             string `envconfig:"PG_FEATURESERV_URL"`
}

// func (cfg Config) AWSConfig() aws.Config {

// 	a := aws.NewConfig().WithRegion(cfg.AWSS3Region)

// 	// Used for "minio" during development
// 	a.WithDisableSSL(cfg.AWSS3DisableSSL)
// 	a.WithS3ForcePathStyle(cfg.AWSS3ForcePathStyle)
// 	if cfg.AWSS3Endpoint != "" {
// 		a.WithEndpoint(cfg.AWSS3Endpoint)
// 	}
// 	return *a
// }

// GetConfig returns environment variable config
func GetConfig() (*Config, error) {
	var cfg Config
	if err := envconfig.Process("cumulus", &cfg); err != nil {
		log.Fatal(err.Error())
	}
	// Fallback for download-link signing: if no dedicated secret is configured,
	// reuse ApplicationKey (already present in every environment) so signed
	// links keep working without an infra change. Setting a dedicated
	// CUMULUS_DOWNLOAD_LINK_SECRET later transparently takes precedence.
	if cfg.DownloadLinkSecret == "" {
		cfg.DownloadLinkSecret = cfg.ApplicationKey
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
