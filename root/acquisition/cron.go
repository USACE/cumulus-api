package acquisition

import (
	"log"
	"time"

	"github.com/robfig/cron"
)

func cronNextRun(cronExpr string) time.Time {
	schedule, err := cron.ParseStandard(cronExpr)
	if err != nil {
		log.Panicf(err.Error())
	}

	// next cron run
	return schedule.Next(time.Now())
}

// CronShouldRunNow returns a boolean based on comparing a cron expression
// for example "* 5 * * *" with the current time and a tolerance.
// The tolerance is a string following syntax that can be handled by time.ParseDuration(),
// for example "10s" or "5m" or "5m30s"
func CronShouldRunNow(cronExpr string, tolerance string) bool {

	// tolerance parsed to milliseconds
	tol, err := time.ParseDuration(tolerance)
	if err != nil {
		log.Printf("Invalid tolerance string for acquisition: %s", tolerance)
		return false
	}

	if cronNextRun(cronExpr).Sub(time.Now()).Milliseconds() < tol.Milliseconds() {
		return true
	}

	return false
}
