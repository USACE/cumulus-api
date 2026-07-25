package handlers

import (
	"log"
	"sync"
	"time"

	"github.com/USACE/cumulus-api/api/models"

	"github.com/jackc/pgx/v5/pgxpool"
)

// Cache serves the result of an expensive load function from memory and
// refreshes it in the background on a fixed interval.
//
// It exists for the product list and product-ingest-status endpoints, both
// backed by views (v_product / v_product_status) whose per-product rollups
// aggregate the entire (multi-million-row) productfile table. Running those on
// every request is what saturated the database's I/O. This cache runs the load
// at most once per interval, in the background, so it never lands on the
// request path: requests are served the last good snapshot instantly and never
// block on the database. A refresh that errors keeps the previous snapshot
// (serve-stale).
type Cache[T any] struct {
	name     string
	interval time.Duration
	load     func() (T, error)

	mu       sync.RWMutex
	val      T
	loaded   bool
	loadedAt time.Time
}

// NewCache creates a cache over load; call Start to warm it and begin
// refreshing. name is used only in log lines.
func NewCache[T any](name string, interval time.Duration, load func() (T, error)) *Cache[T] {
	return &Cache[T]{name: name, interval: interval, load: load}
}

// Start loads once synchronously (so the cache is warm before the server takes
// traffic), then refreshes every interval. A failed initial load is non-fatal:
// Get falls back to a direct load until a refresh succeeds.
func (c *Cache[T]) Start() {
	if err := c.refresh(); err != nil {
		log.Printf("cache %q: initial load failed: %v", c.name, err)
	}
	go func() {
		t := time.NewTicker(c.interval)
		defer t.Stop()
		for range t.C {
			if err := c.refresh(); err != nil {
				log.Printf("cache %q: refresh failed, serving stale (age %s): %v",
					c.name, time.Since(c.loadedAt).Round(time.Second), err)
			}
		}
	}()
}

// refresh reloads the value; the snapshot is only replaced on success.
func (c *Cache[T]) refresh() error {
	v, err := c.load()
	if err != nil {
		return err
	}
	c.mu.Lock()
	c.val = v
	c.loaded = true
	c.loadedAt = time.Now()
	c.mu.Unlock()
	return nil
}

// Get returns the last good value. If the cache has never loaded successfully,
// it loads synchronously this once so callers never receive an empty result on
// a cold cache (returning the load error if that also fails).
func (c *Cache[T]) Get() (T, error) {
	c.mu.RLock()
	if c.loaded {
		v := c.val
		c.mu.RUnlock()
		return v, nil
	}
	c.mu.RUnlock()
	return c.load()
}

// NewProductCache builds the cache backing GET /products.
func NewProductCache(db *pgxpool.Pool, interval time.Duration) *Cache[[]models.Product] {
	return NewCache("products", interval, func() ([]models.Product, error) {
		return models.ListProducts(db)
	})
}

// NewProductStatusCache builds the cache backing GET /product_ingest_status.
func NewProductStatusCache(db *pgxpool.Pool, interval time.Duration) *Cache[[]models.ProductStatus] {
	return NewCache("product_ingest_status", interval, func() ([]models.ProductStatus, error) {
		return models.GetProductIngestStatus(db)
	})
}
