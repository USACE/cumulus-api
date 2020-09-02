package acquirable

import (
	"fmt"
	"time"
)

// RtmaRuAnlAcquirable is RTMA Rapid Update ANL (Analysis?) Product
type RtmaRuAnlAcquirable struct {
	info Info
}

// RtmaRuGesAcquirable is RTMA Rapid Update GES Product
type RtmaRuGesAcquirable struct {
	info Info
}

// RtmaRuURLS returns URLS
func RtmaRuURLS(p string, t *time.Time) []string {

	ymd, hour := t.Format("20060102"), t.Format("15")
	urlBase := fmt.Sprintf("https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtma/prod/rtma2p5_ru.%s", ymd)

	urls := make([]string, 4)
	for idx, minute := range []string{"00z", "15z", "30z", "45z"} {
		urls[idx] = fmt.Sprintf("%s/rtma2p5_ru.t%s%s.2dvar%s_ndfd.grb2", urlBase, hour, minute, p)
	}
	return urls
}

// RTMA Rapid Update ANL
////////////////////////

// URLS implements Acquirable interface
func (a *RtmaRuAnlAcquirable) URLS() []string {
	t := time.Now().Add(time.Hour * -1)
	return RtmaRuURLS("anl", &t)
}

// Info implements Acquirable interface
func (a *RtmaRuAnlAcquirable) Info() Info {
	return a.info
}

// RTMA Rapid Update GES
////////////////////////

// URLS implements Acquirable interface
func (a *RtmaRuGesAcquirable) URLS() []string {
	t := time.Now().Add(time.Hour * -1)
	return RtmaRuURLS("ges", &t)
}

// Info implements Acquirable interface
func (a *RtmaRuGesAcquirable) Info() Info {
	return a.info
}
