package handlers

import (
	"errors"
	"net/http"
	"strings"

	"github.com/USACE/cumulus-api/api/middleware"
	"github.com/google/uuid"
	"github.com/labstack/echo/v4"
)

func GetSub(c echo.Context) (*uuid.UUID, error) {
	userInfo, ok := c.Get("userInfo").(middleware.UserInfo)
	if !ok {
		return nil, errors.New("Could not unmarshal userInfo")
	}
	return userInfo.Sub, nil
}

// GetIdentityProviderConfiguration returns the Keycloak configuration based on the auth environment and realm
func GetIdentityProviderConfiguration(authEnv string, c echo.Context) error {

	// Convert the authEnv to lowercase to make the comparison case-insensitive
	authEnv = strings.ToLower(authEnv)

	// Set the base URL for Keycloak depending on the environment
	var keycloakHost string
	realm := "cwbi" // Set the realm as a variable

	// Determine the Keycloak host based on the authEnv passed
	switch authEnv {
	// ----------------------------
	// Satisfy local mocking
	case "mock":
		keycloakHost = "http://localhost"
	// ----------------------------
	// Castle Cloud auth servers
	case "develop":
		keycloakHost = "https://develop-auth.corps.cloud"
		realm = "water"
	case "stable":
		keycloakHost = "https://auth.corps.cloud"
		realm = "water"
	// ----------------------------
	// CWBI auth servers
	case "dev":
		keycloakHost = "https://identityc-test.cwbi.us"
	case "test":
		keycloakHost = "https://identityc-test.cwbi.us"
	case "prod":
		keycloakHost = "https://identityc.sec.usace.army.mil"
	default:
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid auth environment: " + authEnv,
		})
	}

	// Prepare the configuration as a map of string keys and values
	config := map[string]string{
		"token_endpoint":      keycloakHost + "/auth/realms/" + realm + "/protocol/openid-connect/token",
		"well_known_endpoint": keycloakHost + "/auth/realms/" + realm + "/.well-known/openid-configuration",
	}

	// Return the configuration as a JSON response
	return c.JSON(http.StatusOK, config)
}
