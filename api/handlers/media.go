package handlers

import (
	"context"
	"net/http"
	"net/url"
	"path/filepath"
	"strings"

	_config "github.com/USACE/cumulus-api/api/config"

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

func ServeMedia(awsCfg aws.Config, cfg _config.Config) echo.HandlerFunc {
	return func(c echo.Context) error {
		path, err := cleanFilepath(c.Request().RequestURI)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}

		client := s3.NewFromConfig(awsCfg,
			func(o *s3.Options) {
				o.UsePathStyle = cfg.UsePathStyle
			})

		output, err := client.GetObject(context.TODO(), &s3.GetObjectInput{Bucket: &cfg.AWSS3Bucket, Key: aws.String(path)})
		if err != nil {
			return c.String(500, err.Error())
		}

		c.Response().Header().Set(echo.HeaderContentDisposition, "attachment")
		return c.Stream(http.StatusOK, "application/octet-stream", output.Body)
	}
}
