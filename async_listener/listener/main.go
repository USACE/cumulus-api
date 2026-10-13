package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/USACE/cumulus-api/listener/dispatch"
	"github.com/kelseyhightower/envconfig"
	"github.com/lib/pq"
)

// Message holds Fn (function name) and details (string to send to queue / used by specific worker)
type Message struct {
	Fn      string `json:"fn"`
	Details string `json:"details"`
}

// NotificationHandler is a function that takes a notification and returns an error
type NotificationHandler func(string) error

// Config holds application configuration variables
type Config struct {
	DBUser                      string
	DBPass                      string
	DBName                      string
	DBHost                      string
	DBSSLMode                   string `default:"require"`
	AsyncEnginePackager         string `envconfig:"ASYNC_ENGINE_PACKAGER"`
	AsyncEnginePackagerTarget   string `envconfig:"ASYNC_ENGINE_PACKAGER_TARGET"`
	AsyncEngineStatistics       string `envconfig:"ASYNC_ENGINE_STATISTICS"`
	AsyncEngineStatisticsTarget string `envconfig:"ASYNC_ENGINE_STATISTICS_TARGET"`
	AsyncEngineGeoprocess       string `envconfig:"ASYNC_ENGINE_GEOPROCESS"`
	AsyncEngineGeoprocessTarget string `envconfig:"ASYNC_ENGINE_GEOPROCESS_TARGET"`
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

// sendTimeout bounds a single dispatch. go-simple-asyncer had no timeout at
// all, so a hung send leaked its goroutine for the life of the process.
const sendTimeout = 30 * time.Second

// NewAsyncNotificationHandler handles dependency injection of dispatch.Sender
func NewAsyncNotificationHandler(s dispatch.Sender) NotificationHandler {
	return func(d string) error {
		ctx, cancel := context.WithTimeout(context.Background(), sendTimeout)
		defer cancel()
		if err := s.Send(ctx, []byte(d)); err != nil {
			fmt.Println("Error dispatching to worker queue")
			fmt.Println(err.Error())
			return err
		}
		return nil
	}
}

func waitForNotification(l *pq.Listener, handlers map[string]NotificationHandler) {
	select {
	case n := <-l.Notify:
		fmt.Println("notification on channel: " + n.Channel)
		var m Message
		if err := json.Unmarshal([]byte(n.Extra), &m); err != nil {
			fmt.Printf("ERROR: %s\n", err.Error())
		}
		if handler, ok := handlers[m.Fn]; ok {
			go handler(m.Details)
		} else {
			fmt.Printf("Unimplemented handler for Function (fn) %s\n", m.Fn)
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

	ctx := context.Background()

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

	// downloadAsyncer defines async engine used to package DSS files for download
	downloadSender, err := dispatch.New(ctx, cfg.AsyncEnginePackager, cfg.AsyncEnginePackagerTarget)
	if err != nil {
		log.Fatal(err.Error())
	}
	d := NewAsyncNotificationHandler(downloadSender)

	// acquirablefileAsyncer defines async engine for processing new acquirable files
	geoprocessSender, err := dispatch.New(ctx, cfg.AsyncEngineGeoprocess, cfg.AsyncEngineGeoprocessTarget)
	if err != nil {
		log.Fatal(err.Error())
	}
	g := NewAsyncNotificationHandler(geoprocessSender)

	// statisticsAsyncer defines async engine for computing raster statistics
	// statisticsSender, err := dispatch.New(ctx, cfg.AsyncEngineStatistics, cfg.AsyncEngineStatisticsTarget)
	// if err != nil {
	// 	log.Fatal(err.Error())
	// }
	// // AddstatisticsAsyncer to map of registered handlers
	// handlers["notify_statistics"] = NewAsyncNotificationHandler(statisticsSender)

	// Map of handlers
	handlers := map[string]NotificationHandler{
		"geoprocess-acquirablefile":     g,
		"geoprocess-snodas-interpolate": g,
		"new-download":                  d,
	}

	fmt.Println("entering main loop")
	for {
		waitForNotification(listener, handlers)
	}
}
