package handlers

// import (
// 	"net/http"

// 	"github.com/google/uuid"
// 	"github.com/jmoiron/sqlx"
// 	"github.com/labstack/echo/v4"
// 	"github.com/lib/pq"

// 	"api/models"
// )

// // ListMyWatersheds returns a list of watersheds linked to the logged-in profile
// func ListMyWatersheds(db *sqlx.DB) echo.HandlerFunc {
// 	return func(c echo.Context) error {
// 		p, err := profileFromContext(c, db)
// 		if err != nil {
// 			return c.JSON(http.StatusBadRequest, err)
// 		}
// 		ww, err := models.ListMyWatersheds(db, &p.ID)
// 		if err != nil {
// 			return c.JSON(http.StatusInternalServerError, err)
// 		}
// 		return c.JSON(http.StatusOK, ww)
// 	}
// }

// // MyWatershedsAdd links a watershed to logged-in profile
// func MyWatershedsAdd(db *sqlx.DB) echo.HandlerFunc {
// 	return func(c echo.Context) error {
// 		// Profile
// 		p, err := profileFromContext(c, db)
// 		if err != nil {
// 			return c.JSON(http.StatusBadRequest, err)
// 		}
// 		// Watershed ID From URL
// 		watershedID, err := uuid.Parse(c.Param("watershed_id"))
// 		if err != nil {
// 			return c.JSON(http.StatusBadRequest, err)
// 		}
// 		if err := models.MyWatershedsAdd(db, &p.ID, &watershedID); err != nil {
// 			if err, ok := err.(*pq.Error); ok {
// 				switch err.Code {
// 				// Profile already subscribed to watershed; Return a RESTful 200;
// 				// i.e. nothing wrong, state of data is already "added"
// 				case "23505":
// 					return c.JSON(http.StatusOK, make(map[string]interface{}))
// 				default:
// 					return c.JSON(http.StatusInternalServerError, err)
// 				}
// 			}
// 			return c.JSON(http.StatusInternalServerError, err)
// 		}
// 		return c.JSON(http.StatusOK, make(map[string]interface{}))
// 	}
// }

// // MyWatershedsRemove links a watershed to logged-in profile
// func MyWatershedsRemove(db *sqlx.DB) echo.HandlerFunc {
// 	return func(c echo.Context) error {
// 		// Profile
// 		p, err := profileFromContext(c, db)
// 		if err != nil {
// 			return c.JSON(http.StatusBadRequest, err)
// 		}
// 		// Watershed ID From URL
// 		watershedID, err := uuid.Parse(c.Param("watershed_id"))
// 		if err != nil {
// 			return c.JSON(http.StatusBadRequest, err)
// 		}
// 		err = models.MyWatershedsRemove(db, &p.ID, &watershedID)
// 		if err != nil {
// 			return c.String(http.StatusInternalServerError, err.Error())
// 		}
// 		return c.JSON(http.StatusOK, make(map[string]interface{}))
// 	}
// }
