package handlers

import (
	"context"
	"net/http"
	"net/url"
	"path"
	"strings"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/labstack/echo/v4"
)

func cleanFilepath(rawPath string) (string, error) {
	p, err := url.PathUnescape(rawPath)
	if err != nil {
		return "", err
	}
	// The download route is mounted under the /api group; strip that prefix to
	// recover the S3 key.
	p = strings.TrimPrefix(p, "/api")
	// S3 keys are exact, literal strings under the aws-sdk-go-v2 client: a leading
	// slash makes "/cumulus/..." a different key than the stored "cumulus/..." and
	// real S3 returns NoSuchKey (the v1 SDK and MinIO normalize it, hiding this).
	// path.Clean still resolves any ".." for traversal safety.
	return strings.TrimPrefix(path.Clean("/"+p), "/"), nil
}

func ServeMedia(awsCfg *aws.Config, bucket *string, forcePathStyle bool) echo.HandlerFunc {
	return func(c echo.Context) error {
		path, err := cleanFilepath(c.Request().RequestURI)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}

		_client := s3.NewFromConfig(
			*awsCfg,
			func(o *s3.Options) {
				o.UsePathStyle = forcePathStyle // was a.WithS3ForcePathStyle(...)
			})
		output, err := _client.GetObject(context.Background(), &s3.GetObjectInput{Bucket: bucket, Key: aws.String(path)})
		if err != nil {
			return c.String(500, err.Error())
		}

		c.Response().Header().Set(echo.HeaderContentDisposition, "attachment")
		return c.Stream(http.StatusOK, "application/octet-stream", output.Body)
	}
}
