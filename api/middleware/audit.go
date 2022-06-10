package middleware

import (
	"net/http"

	"github.com/golang-jwt/jwt"
	"github.com/google/uuid"

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
			Sub: &anonUUID,
			Roles: []string{},
			IsAdmin: false,
		})
		return next(c)
	}
}

func AttachUserInfo(next echo.HandlerFunc) echo.HandlerFunc {
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
		return next(c)
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
