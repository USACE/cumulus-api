package handlers

import (
	"context"
	"net/http"
	"net/url"
	"path/filepath"
	"strings"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/labstack/echo/v4"
)

func cleanFilepath(rawPath string) (string, error) {
	p, err := url.PathUnescape(rawPath)
	// Replace /api with /
	p = strings.Replace(p, "/api", "/", 1)
	if err != nil {
		return "", err
	}
	return filepath.Clean("/" + p), nil
}

func ServeMedia(awsCfg *aws.Config, bucket *string, endpoint string, forcePathStyle, disableSSL bool) echo.HandlerFunc {
	return func(c echo.Context) error {
		path, err := cleanFilepath(c.Request().RequestURI)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}

		_client := s3.NewFromConfig(*awsCfg, func(o *s3.Options) {
			o.UsePathStyle = forcePathStyle // was a.WithS3ForcePathStyle(...)
			if endpoint != "" {             // was: if cfg.AWSS3Endpoint != "" { a.WithEndpoint(...) }
				o.BaseEndpoint = aws.String(endpoint)
			}
			if disableSSL { // was a.WithDisableSSL(...)
				o.EndpointOptions.DisableHTTPS = true
			}
		})
		output, err := _client.GetObject(context.Background(), &s3.GetObjectInput{Bucket: bucket, Key: aws.String(path)})
		if err != nil {
			return c.String(500, err.Error())
		}

		c.Response().Header().Set(echo.HeaderContentDisposition, "attachment")
		return c.Stream(http.StatusOK, "application/octet-stream", output.Body)
	}
}
