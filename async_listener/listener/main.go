package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/USACE/go-simple-asyncer/asyncer"
	"github.com/google/uuid"
	"github.com/jmoiron/sqlx"
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

// NewProductfileMessage holds database notification information for New Productfile Created
type NewProductfileMessage struct {
	ProductfileID uuid.UUID `json:"productfile_id" db:"productfile_id"`
	ProductID     uuid.UUID `json:"product_id" db:"product_id"`
	S3Bucket      string    `json:"s3_bucket" db:"s3_bucket"`
	S3Key         string    `json:"s3_key" db:"s3_key"`
}

func handleStatistics(n *pq.Notification, db *sqlx.DB, statistics asyncer.Asyncer) error {
	var m NewProductfileMessage
	if err := json.Unmarshal([]byte(n.Extra), &m); err != nil {
		fmt.Println("error unmarshaling new productfile message")
		return err
	}
	// Select list of basin IDs subscribed to statistics for the product
	// that have a valid geometry that can be used to calculate statistics
	sql := `SELECT a.basin_id
	        FROM basin_product_statistics_enabled a
			INNER JOIN v_basin_5070 b ON b.id = a.basin_id
			WHERE b.geometry IS NOT NULL AND a.product_id = $1
			`
	bb := make([]uuid.UUID, 0)
	if err := db.Select(&bb, sql, m.ProductID); err != nil {
		fmt.Println("Eror querying database")
		fmt.Println(err.Error())
		return err
	}

	// Create a Message to Compute statistics for each basin
	for _, b := range bb {
		payload, err := json.Marshal(map[string]string{
			"productfile_id": m.ProductfileID.String(),
			"basin_id":       b.String(),
			"s3_key":         m.S3Key,
			"s3_bucket":      m.S3Bucket,
		})
		if err != nil {
			fmt.Println("Error in marshalling payload")
			return err
		}
		// Send message
		if err := statistics.CallAsync(payload); err != nil {
			fmt.Println("Error calling statistics async")
			fmt.Println(err.Error())
			return err
		}
	}
	return nil
}

func waitForNotification(l *pq.Listener, db *sqlx.DB, statistics asyncer.Asyncer, packager asyncer.Asyncer) {
	select {
	case n := <-l.Notify:
		fmt.Println("notification on channel: " + n.Channel)
		if n.Channel == "cumulus_new_productfile" {
			go handleStatistics(n, db, statistics)
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

	// Database Connection
	db := sqlx.MustOpen("postgres", cfg.connStr())

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

	// Start Listening
	if err := listener.Listen("cumulus_new_productfile"); err != nil {
		panic(err)
	}

	fmt.Println("entering main loop")
	for {
		waitForNotification(listener, db, statisticsAsyncer, packagerAsyncer)
	}
}
