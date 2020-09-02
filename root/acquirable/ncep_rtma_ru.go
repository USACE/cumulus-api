package acquirable

import (
	"fmt"
	"time"
)

// NcepRtmaRuAnlAcquirable is RTMA Rapid Update ANL (Analysis?) Product
type NcepRtmaRuAnlAcquirable struct {
	info Info
}

// NcepRtmaRuGesAcquirable is RTMA Rapid Update GES Product
type NcepRtmaRuGesAcquirable struct {
	info Info
}

// NcepRtmaRuURLS returns URLS
func NcepRtmaRuURLS(p string, t *time.Time) []string {

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
func (a *NcepRtmaRuAnlAcquirable) URLS() []string {
	t := time.Now().Add(time.Hour * -1)
	return NcepRtmaRuURLS("anl", &t)
}

// Info implements Acquirable interface
func (a *NcepRtmaRuAnlAcquirable) Info() Info {
	return a.info
}

// RTMA Rapid Update GES
////////////////////////

// URLS implements Acquirable interface
func (a *NcepRtmaRuGesAcquirable) URLS() []string {
	t := time.Now().Add(time.Hour * -1)
	return NcepRtmaRuURLS("ges", &t)
}

// Info implements Acquirable interface
func (a *NcepRtmaRuGesAcquirable) Info() Info {
	return a.info
}
