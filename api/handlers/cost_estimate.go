package handlers

import (
	"net/http"

	"github.com/USACE/cumulus-api/api/costs"
	"github.com/USACE/cumulus-api/api/models"
	"github.com/labstack/echo/v4"
)

// GetCostEstimate returns the estimated AWS cost of running Cumulus: a
// monthly run rate, year-to-date, and the running total since
// COST_START_DATE, broken down by category.
func GetCostEstimate(est *costs.Estimator) echo.HandlerFunc {
	return func(c echo.Context) error {
		e, err := est.Get(c.Request().Context())
		if err != nil {
			c.Logger().Errorf("cost estimate: %v", err)
			return c.JSON(http.StatusInternalServerError, models.DefaultMessageInternalServerError)
		}
		return c.JSON(http.StatusOK, e)
	}
}
