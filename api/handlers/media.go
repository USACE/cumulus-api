package handlers

import (
	"net/http"
	"net/url"
	"path/filepath"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/labstack/echo/v4"
)

func cleanFilepath(rawPath string) (string, error) {
	p, err := url.PathUnescape(rawPath)
	if err != nil {
		return "", err
	}
	return filepath.Clean("/" + p), nil
}

func ServeMedia(awsCfg *aws.Config, bucket *string) echo.HandlerFunc {
	return func(c echo.Context) error {
		path, err := cleanFilepath(c.Request().RequestURI)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}

		_client := s3.New(session.New(awsCfg))
		output, err := _client.GetObject(&s3.GetObjectInput{Bucket: bucket, Key: aws.String(path)})
		if err != nil {
			return c.String(500, err.Error())
		}

		c.Response().Header().Set(echo.HeaderContentDisposition, "attachment")
		return c.Stream(http.StatusOK, "application/octet-stream", output.Body)
	}
}
