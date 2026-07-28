package middleware

import (
	"context"
	"time"

	"github.com/labstack/echo/v4"
)

// streamingRoutes are the routes whose responses are open-ended byte streams:
// packaged download files and range-served COGs. They are listed by echo route
// pattern (c.Path()), not by request URL, so a rename of a path parameter can't
// silently unmatch them.
//
// These must never get a request deadline. The deadline cancels the request
// context, which is what the S3 read is bound to, so a large .dss package or a
// slow COG range read would be truncated partway through -- the client sees a
// short file rather than an error.
var streamingRoutes = map[string]bool{
	"/api/downloads/:download_id/file":              true,
	"/api/downloads/:download_id/file/:filename":    true,
	"/api/products/:product_id/cog/:productfile_id": true,
}

// SkipStreamingRoutes reports whether the matched route streams a response body
// of unbounded size and should therefore be exempt from RequestTimeout.
func SkipStreamingRoutes(c echo.Context) bool {
	// Normalize the leading slash rather than depending on whether echo added one
	// when joining the "api" group prefix: a lookup that silently misses here
	// re-arms the deadline on exactly the routes that must not have it.
	p := c.Path()
	if p != "" && p[0] != '/' {
		p = "/" + p
	}
	return streamingRoutes[p]
}

// RequestTimeout puts a hard deadline on the request context so that work
// started on a request's behalf stops when the request does.
//
// This matters because c.Request().Context() on its own is only cancelled when
// the *client* disappears -- a patient client means no deadline at all. Handlers
// and the models layer must pass this context down (pgxpool.Acquire and every
// pgx query take one) for it to have any effect; a query invoked with
// context.Background() keeps running and keeps holding its pool connection no
// matter what this middleware does.
//
// Deliberately not echo's middleware.Timeout(): that wraps http.TimeoutHandler,
// which races with streaming responses and, more to the point, does not cancel
// the database work underneath -- it only stops waiting for it.
func RequestTimeout(d time.Duration, skipper func(echo.Context) bool) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if d <= 0 || (skipper != nil && skipper(c)) {
				return next(c)
			}
			ctx, cancel := context.WithTimeout(c.Request().Context(), d)
			// Releases the timer as soon as the handler returns; without this the
			// timer stays armed for the full duration on every fast request.
			defer cancel()

			c.SetRequest(c.Request().WithContext(ctx))
			return next(c)
		}
	}
}
