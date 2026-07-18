package middleware

import (
	"context"
	"log"
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/USACE/cumulus-api/api/models"
	"github.com/labstack/echo/v4"
)

var (
	applicationAdminRole = "application.admin"
)

type UserInfo struct {
	Sub     *uuid.UUID `json:"sub"`
	Roles   []string   `json:"roles"`
	IsAdmin bool       `json:"is_admin"`
}

func AttachAnonymousUserInfo(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		anonUUID := uuid.MustParse("11111111-1111-1111-1111-111111111111")
		c.Set("userInfo", UserInfo{
			Sub:     &anonUUID,
			Roles:   []string{},
			IsAdmin: false,
		})
		return next(c)
	}
}

// claimStr returns claims[key] as *string, or nil if absent/not a string.
func claimStr(claims jwt.MapClaims, key string) *string {
	if v, ok := claims[key].(string); ok && v != "" {
		return &v
	}
	return nil
}

func AttachUserInfo(db *pgxpool.Pool) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			keyAuthSuccess, ok := c.Get("ApplicationKeyAuthSuccess").(bool)
			if ok && keyAuthSuccess {
				userInfo := UserInfo{
					Sub:     nil,
					Roles:   []string{applicationAdminRole},
					IsAdmin: true,
				}
				c.Set("userInfo", userInfo)
				return next(c)
			}
			// JWT
			user := c.Get("user").(*jwt.Token)
			claims := user.Claims.(jwt.MapClaims)
			// Parse 'sub to UUID
			subStr := claims["sub"].(string)
			sub, err := uuid.Parse(subStr)
			if err != nil {
				return c.JSON(http.StatusInternalServerError, map[string]string{})
			}
			resourceAccess := claims["resource_access"].(map[string]interface{})
			// Cumulus Specific
			cumulusResourceAccess := resourceAccess["cumulus"].(map[string]interface{})
			cumulusRoles := cumulusResourceAccess["roles"].([]interface{})
			// Attach Role Info
			userInfo := UserInfo{
				Sub:     &sub,
				Roles:   make([]string, 0),
				IsAdmin: false,
			}
			for _, r := range cumulusRoles {
				rStr, ok := r.(string)
				if !ok {
					return c.JSON(http.StatusInternalServerError, map[string]string{})
				}
				userInfo.Roles = append(userInfo.Roles, rStr)
				if rStr == applicationAdminRole {
					userInfo.IsAdmin = true
				}
			}
			c.Set("userInfo", userInfo)

			// Best-effort, non-blocking refresh of the display-name cache. A lost
			// update on process crash just leaves a stale display name until the
			// next request; not worth adding request latency to guard against.
			preferredUsername := claimStr(claims, "preferred_username")
			email := claimStr(claims, "email")
			name := claimStr(claims, "name")
			go func(sub uuid.UUID, preferredUsername, email, name *string) {
				// Detached goroutine: recover so a panic here can never take down
				// the process (no global Recover middleware is registered), and
				// bound the DB call so a slow database can't pile these up against
				// the connection pool.
				defer func() {
					if r := recover(); r != nil {
						log.Printf("user_directory upsert panic for sub %s: %v", sub, r)
					}
				}()
				ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
				defer cancel()
				if err := models.UpsertUserDirectory(ctx, db, sub, preferredUsername, email, name); err != nil {
					log.Printf("user_directory upsert failed for sub %s: %v", sub, err)
				}
			}(sub, preferredUsername, email, name)

			return next(c)
		}
	}
}

func IsAdmin(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		userInfo, ok := c.Get("userInfo").(UserInfo)
		if !ok {
			return c.JSON(http.StatusForbidden, map[string]string{})
		}
		if userInfo.IsAdmin {
			return next(c)
		}
		return c.JSON(http.StatusForbidden, map[string]string{})
	}
}
