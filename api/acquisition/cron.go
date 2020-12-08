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
		log.Printf("Invalid tolerance string: %s", tolerance)
		return false
	}

	// Current Time
	now := time.Now().UTC()
	cronNextRun := cronNextRun(cronExpr).UTC()
	timeUntilCronNextRun := cronNextRun.Sub(now)
	runCron := timeUntilCronNextRun.Milliseconds() < tol.Milliseconds()

	// Log output
	log.Printf("Cron Schedule        : %s", cronExpr)
	log.Printf("Current Time         : %s", now.String())
	log.Printf("Next Cron Run        : %s", cronNextRun.String())
	log.Printf("Time Until Next Cron : %s (Tolerance: %s)", timeUntilCronNextRun.String(), tol.String())
	log.Printf("Cron Should Run Now? : %t", runCron)

	if runCron {
		return true
	}

	return false
}
