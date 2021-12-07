package handlers

import (
	"errors"

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
