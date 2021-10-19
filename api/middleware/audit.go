package middleware

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"

	"github.com/USACE/cumulus-api/api/models"

	jwt "github.com/dgrijalva/jwt-go"
	"github.com/google/uuid"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/labstack/echo/v4"
)

// EDIPIMiddleware attaches EDIPI (CAC) to Context
// Used for CAC-Only Routes
func EDIPIMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		// If key is in query parameters; count on keyauth
		key := c.QueryParam("key")
		if key == "" {
			user := c.Get("user").(*jwt.Token)
			claims := user.Claims.(jwt.MapClaims)
			// Get EDIPI
			EDIPI, err := strconv.Atoi(claims["sub"].(string))
			if err != nil {
				return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
			}
			c.Set("EDIPI", EDIPI)
		}
		return next(c)
	}
}

func CACOnlyMiddleware(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		EDIPI := c.Get("EDIPI")
		if EDIPI == nil {
			return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
		}
		return next(c)
	}
}

// AttachProfileID attaches ProfileID of user to context
func AttachProfileMiddleware(db *pgxpool.Pool) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// If Application "Superuser" authenticated using Key Authentication (?key= query parameter),
			// lookup superuser profile; the "EDIPI" of the Superuser is consistently 79.
			// The superuser is initialized as part of database and seed data initialization
			if c.Get("ApplicationKeyAuthSuccess") == true {
				p, err := models.GetProfileFromEDIPI(db, 29)
				if err != nil {
					return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
				}
				c.Set("profile", p)
				return next(c)
			}
			// If a User was authenticated via KeyAuth, lookup the user's profile using key_id
			if c.Get("KeyAuthSuccess") == true {
				keyID := c.Get("KeyAuthKeyID").(string)
				p, err := models.GetProfileFromTokenID(db, keyID)
				if err != nil {
					return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
				}
				c.Set("profile", p)
				return next(c)
			}
			// If a User was authenticated using CAC (JWT), lookup Profile by EDIPI
			EDIPI := c.Get("EDIPI")
			if EDIPI == nil {
				return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
			}
			p, err := models.GetProfileFromEDIPI(db, EDIPI.(int))
			if err != nil {
				return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
			}
			c.Set("profile", p)

			return next(c)
		}
	}
}

func IsApplicationAdmin(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		p, ok := c.Get("profile").(*models.Profile)
		if !ok {
			return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
		}
		if !p.IsAdmin {
			return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
		}
		return next(c)
	}
}

func IsWatershedAdminMiddleware(db *pgxpool.Pool) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			p, ok := c.Get("profile").(*models.Profile)
			if !ok {
				return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
			}
			// Application Admins Automatic Admin Status for All Watersheds
			if p.IsAdmin {
				return next(c)
			}
			// Lookup watershed from URL Route Parameter
			watershedID, err := uuid.Parse(c.Param("watershed_id"))
			if err != nil {
				return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
			}
			watershed, err := models.GetWatershed(db, &watershedID)
			if err != nil {
				return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
			}
			grantingRole := fmt.Sprintf("%s.ADMIN", strings.ToUpper(watershed.Slug))
			for _, r := range p.Roles {
				if r == grantingRole {
					return next(c)
				}
			}
			return c.JSON(http.StatusForbidden, models.DefaultMessageUnauthorized)
		}
	}
}
