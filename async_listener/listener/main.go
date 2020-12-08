package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/USACE/go-simple-asyncer/asyncer"
	"github.com/google/uuid"
	"github.com/kelseyhightower/envconfig"
	"github.com/lib/pq"
)

// NotificationHandler is a function that takes a notification and returns an error
type NotificationHandler func(*pq.Notification) error

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
	MaxReconn                   string `envconfig:"MAX_RECONN"`
	MinReconn                   string `envconfig:"MIN_RECONN"`
}

// connStr returns a database connection string
func (c Config) connStr() string {
	return fmt.Sprintf(
		"user=%s password=%s dbname=%s host=%s sslmode=%s binary_parameters=yes",
		c.DBUser, c.DBPass, c.DBName, c.DBHost, c.DBSSLMode,
	)
}

func (c Config) minReconn() time.Duration {
	d, err := time.ParseDuration(c.MinReconn)
	if err != nil {
		panic(err.Error())
	}
	return d
}

func (c Config) maxReconn() time.Duration {
	d, err := time.ParseDuration(c.MaxReconn)
	if err != nil {
		panic(err.Error())
	}
	return d
}

// Message holds ID of new record and table/entity name
type Message struct {
	ID    uuid.UUID `json:"id"`
	Table string    `json:"table"`
}

// NewAsyncNotificationHandler handles dependency injection of asyncer.Asyncer
func NewAsyncNotificationHandler(a asyncer.Asyncer) NotificationHandler {
	return func(n *pq.Notification) error {
		if err := a.CallAsync([]byte(n.Extra)); err != nil {
			fmt.Println("Error calling async")
			fmt.Println(err.Error())
			return err
		}
		return nil
	}
}

func waitForNotification(l *pq.Listener, handleDownload, handleStatistics NotificationHandler) {
	select {
	case n := <-l.Notify:
		fmt.Println("notification on channel: " + n.Channel)
		var m Message
		if err := json.Unmarshal([]byte(n.Extra), &m); err != nil {
			print("ERROR: %s", err.Error())
		}
		switch m.Table {
		case "download":
			go handleDownload(n)
		case "statistics":
			go handleStatistics(n)
		default:
			fmt.Printf("Unimplemented handler for new records in table %s", m.Table)
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

	// Database Listener
	listener := pq.NewListener(cfg.connStr(), cfg.minReconn(), cfg.maxReconn(), reportProblem)
	// Start Listening for Productfiles
	if err := listener.Listen("cumulus_new"); err != nil {
		panic(err)
	}

	// packagerAsyncer defines async engine used to package DSS files for download
	downloadAsyncer, err := asyncer.NewAsyncer(asyncer.Config{Engine: cfg.AsyncEnginePackager, Target: cfg.AsyncEnginePackagerTarget})
	if err != nil {
		log.Fatal(err.Error())
	}
	d := NewAsyncNotificationHandler(downloadAsyncer)

	// statisticsAsyncer defines async engine for computing raster statistics
	statisticsAsyncer, err := asyncer.NewAsyncer(asyncer.Config{Engine: cfg.AsyncEngineStatistics, Target: cfg.AsyncEngineStatisticsTarget})
	if err != nil {
		log.Fatal(err.Error())
	}
	s := NewAsyncNotificationHandler(statisticsAsyncer)

	fmt.Println("entering main loop")
	for {
		waitForNotification(listener, d, s)
	}
}
