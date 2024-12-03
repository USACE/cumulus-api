package middleware

import (
	"context"
	"log"
	"net/http"
	"net/url"
	"path"
	"strings"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/labstack/echo/v4"
)

type (
	S3StaticConfig struct {
		// Skipper defines a function to skip middleware. Returning true skips processing
		// the middleware.
		Skipper func(c echo.Context) bool

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

	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) (err error) {
			if staticConfig.Skipper(c) {
				return next(c)
			}

			// get a clean url path
			p := c.Request().URL.Path

			p, err = url.PathUnescape(p)
			if err != nil {
				log.Printf("PathUnescape error: %s\n", err)
				return
			}

			// set the potential key from path and default key incase that does not exist
			pathKey := path.Join(staticConfig.Prefix, path.Clean("/"+p))
			key := path.Join(staticConfig.Prefix, path.Clean("/"+staticConfig.Index))

			// load aws config and get a client
			cfg, err := config.LoadDefaultConfig(context.Background())
			if staticConfig.Environment == "MOCK" {
				cfg, err = config.LoadDefaultConfig(context.Background(),
					config.WithEndpointResolverWithOptions(
						aws.EndpointResolverWithOptionsFunc(
							func(service, region string, options ...any) (aws.Endpoint, error) {
								return aws.Endpoint{
									URL:               staticConfig.Endpoint,
									HostnameImmutable: true,
								}, nil
							}),
					),
				)
			}

			client := s3.NewFromConfig(cfg)

			// first, check if the bucket exists and we have permission to access
			_, err = client.HeadBucket(context.Background(), &s3.HeadBucketInput{Bucket: &staticConfig.Bucket})
			if err != nil {
				log.Printf("no permissions or bucket does not exist: %s", staticConfig.Bucket)
				return
			}

			// get a list of content in the bucket limited on the Prefix
			objects, err := client.ListObjectsV2(context.Background(), &s3.ListObjectsV2Input{
				Bucket: &staticConfig.Bucket,
				Prefix: &staticConfig.Prefix,
			})

			if err != nil {
				log.Printf("ListObjectsV2 error: %s\n", err)
				return
			}

			// check that the incoming path is available
			for _, objContent := range objects.Contents {
				if pathKey == *objContent.Key {
					key = pathKey
					break
				}
			}

			// if available, get and serve
			var obj *s3.GetObjectOutput
			obj, err = client.GetObject(context.Background(), &s3.GetObjectInput{
				Bucket: &staticConfig.Bucket,
				Key:    &key,
			})
			if err != nil {
				log.Printf("GetObject error on key '%s': %s\n", key, err)
				return
			}
			defer obj.Body.Close()

			// stream content
			err = c.Stream(http.StatusOK, *obj.ContentType, obj.Body)
			if err != nil {
				log.Printf("Streaming error for '%s': %s", key, err)
			}

			return err
		}
	}
}
