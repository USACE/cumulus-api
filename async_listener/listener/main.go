package main

import (
	"fmt"
	"log"
	"time"

	"github.com/USACE/go-simple-asyncer/asyncer"
	"github.com/kelseyhightower/envconfig"
	"github.com/lib/pq"
)

// Config holds application configuration variables
type Config struct {
	DBUser                      string
	DBPass                      string
	DBName                      string
	DBHost                      string
	DBSSLMode                   string
	AsyncEnginePackager         string `envconfig:"ASYNC_ENGINE_PACKAGER"`
	AsyncEnginePackagerTarget   string `envconfig:"ASYNC_ENGINE_PACKAGER_TARGET"`
	AsyncEngineStatistics       string `envconfig:"ASYNC_ENGINE_STATISTICS"`
	AsyncEngineStatisticsTarget string `envconfig:"ASYNC_ENGINE_STATISTICS_TARGET"`
}

// connStr returns a database connection string
func connStr(cfg *Config) string {
	return fmt.Sprintf(
		"user=%s password=%s dbname=%s host=%s sslmode=%s binary_parameters=yes",
		cfg.DBUser, cfg.DBPass, cfg.DBName, cfg.DBHost, cfg.DBSSLMode,
	)
}

func waitForNotification(l *pq.Listener, statistics asyncer.Asyncer, packager asyncer.Asyncer) {
	select {
	case n := <-l.Notify:
		fmt.Println("received notification; channel: " + n.Channel)
		err := statistics.CallAsync([]byte(n.Extra))
		if err != nil {
			fmt.Println(err)
		}
	case <-time.After(90 * time.Second):
		go l.Ping()
		fmt.Println("received no work for 90 seconds; checking for new work")
	}
}

func reportProblem(eq pq.ListenerEventType, err error) {
	if err != nil {
		fmt.Println(err.Error())
	}
}

func main() {

	var cfg Config
	if err := envconfig.Process("cumulus", &cfg); err != nil {
		log.Fatal(err.Error())
	}

	// packagerAsyncer defines async engine used to package DSS files for download
	packagerAsyncer, err := asyncer.NewAsyncer(
		asyncer.Config{Engine: cfg.AsyncEnginePackager, Target: cfg.AsyncEnginePackagerTarget},
	)
	if err != nil {
		log.Fatal(err.Error())
	}

	// statisticsAsyncer defines async engine for computing raster statistics
	statisticsAsyncer, err := asyncer.NewAsyncer(
		asyncer.Config{Engine: cfg.AsyncEngineStatistics, Target: cfg.AsyncEngineStatisticsTarget},
	)

	minReconn := 10 * time.Second
	maxReconn := time.Minute
	listener := pq.NewListener(
		connStr(&cfg), minReconn, maxReconn, reportProblem,
	)

	if err := listener.Listen("cumulus_productfile_statistics"); err != nil {
		panic(err)
	}

	fmt.Println("entering main loop")
	for {
		waitForNotification(listener, statisticsAsyncer, packagerAsyncer)
	}
}
