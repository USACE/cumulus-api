package middleware

import (
	"log"
	"net/http"
	"net/url"
	"path"
	"strings"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/labstack/echo/v4"
)

type (
	S3StaticConfig struct {
		// Skipper defines a function to skip middleware. Returning true skips processing
		// the middleware.
		Skipper func(c echo.Context) bool

		// AwsConfig is the process-wide AWS configuration. Supplying it here lets
		// the middleware build its S3 client once at startup instead of resolving
		// credentials on every request.
		// Required.
		AwsConfig aws.Config

		// UsePathStyle enables path-style addressing
		// (https://s3.amazonaws.com/BUCKET/KEY) instead of the default virtual
		// hosted-bucket form (https://BUCKET.s3.amazonaws.com/KEY).
		UsePathStyle bool

		// S3 bucket.
		// Required.
		Bucket string `yaml:"bucket"`

		// Prefix limits the response to keys that begin with the specified prefix.
		// Optional. Default value "/"
		Prefix string `yaml:"prefix"`

		// Index file for serving content.
		// Optional. Default value "index.html".
		Index string `yaml:"index"`

		// Working Environment.
		Environment string `yaml:"environment"`

		// S3 Endpoint
		Endpoint string
	}
)

var (
	DefaultS3StaticConfig = S3StaticConfig{
		Skipper: DefaultSkipper,
		Index:   "index.html",
		Prefix:  "/",
	}
)

// DefaultSkipper returns false which processes the middleware.
func DefaultSkipper(echo.Context) bool {
	return false
}

// objectKey joins the configured prefix with a request path and strips any
// leading slash. aws-sdk-go-v2 sends keys verbatim, so "/index.html" names a
// different (and almost certainly absent) object than "index.html" on real S3 --
// a mismatch that hides locally because MinIO tolerates it. The default Prefix
// of "/" makes path.Join produce exactly that leading-slash form.
func objectKey(prefix, p string) string {
	return strings.TrimPrefix(path.Join(prefix, path.Clean("/"+p)), "/")
}

// S3Satic
func S3Satic(S3StaticConfig S3StaticConfig) echo.MiddlewareFunc {
	c := DefaultS3StaticConfig
	return S3StaticWithConfig(c)
}

// S3StaticWithConfig returns S3Static middleware with config
// See `S3Static()`
func S3StaticWithConfig(staticConfig S3StaticConfig) echo.MiddlewareFunc {
	if staticConfig.Skipper == nil {
		staticConfig.Skipper = DefaultS3StaticConfig.Skipper
	}
	if staticConfig.Index == "" {
		staticConfig.Index = DefaultS3StaticConfig.Index
	}
	if staticConfig.Prefix == "" {
		staticConfig.Prefix = DefaultS3StaticConfig.Prefix
	}
	if !strings.HasSuffix(staticConfig.Prefix, "/") {
		staticConfig.Prefix += "/"
	}
	if strings.HasPrefix(staticConfig.Prefix, "/") && staticConfig.Prefix != "/" {
		staticConfig.Prefix = strings.TrimPrefix(staticConfig.Prefix, "/")
	}

	// Build the S3 client once, at middleware construction. The previous version
	// called config.LoadDefaultConfig and s3.NewFromConfig inside the request
	// handler, so every static asset request built a fresh credential provider
	// with an empty cache -- forcing a credential lookup (an IMDS/STS round trip
	// on EC2/ECS) before any S3 call could even be signed -- and allocated a new
	// connection pool that was discarded at the end of the request.
	client := s3.NewFromConfig(staticConfig.AwsConfig, func(o *s3.Options) {
		o.UsePathStyle = staticConfig.UsePathStyle
		// Local MinIO. In every other environment the endpoint comes from the
		// shared config (AWS_ENDPOINT_URL_S3 or the region default).
		if staticConfig.Environment == "MOCK" && staticConfig.Endpoint != "" {
			o.BaseEndpoint = aws.String(staticConfig.Endpoint)
		}
	})

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if staticConfig.Skipper(c) {
				return next(c)
			}
			ctx := c.Request().Context()

			// get a clean url path
			p, err := url.PathUnescape(c.Request().URL.Path)
			if err != nil {
				log.Printf("PathUnescape error: %s", err)
				return echo.NewHTTPError(http.StatusBadRequest)
			}

			// set the potential key from path and default key incase that does not exist
			pathKey := objectKey(staticConfig.Prefix, p)
			key := objectKey(staticConfig.Prefix, staticConfig.Index)

			// Serve the requested key if it exists, otherwise fall back to the SPA
			// index. A single HeadObject replaces the previous HeadBucket +
			// ListObjectsV2 pair. Besides being two fewer round trips, it is correct
			// for buckets holding more than 1000 keys under the prefix -- the list
			// call returned only the first page, so any asset past that boundary was
			// silently served the index instead of itself.
			if _, err := client.HeadObject(ctx, &s3.HeadObjectInput{
				Bucket: &staticConfig.Bucket,
				Key:    &pathKey,
			}); err == nil {
				key = pathKey
			}

			obj, err := client.GetObject(ctx, &s3.GetObjectInput{
				Bucket: &staticConfig.Bucket,
				Key:    &key,
			})
			if err != nil {
				log.Printf("GetObject error on key '%s': %s", key, err)
				return echo.NewHTTPError(http.StatusNotFound)
			}
			defer obj.Body.Close()

			// S3 omits ContentType for objects uploaded without one; dereferencing it
			// blindly panicked the process, since no Recover middleware is registered.
			contentType := "application/octet-stream"
			if obj.ContentType != nil {
				contentType = *obj.ContentType
			}

			// stream content
			if err := c.Stream(http.StatusOK, contentType, obj.Body); err != nil {
				log.Printf("Streaming error for '%s': %s", key, err)
				return err
			}
			return nil
		}
	}
}
