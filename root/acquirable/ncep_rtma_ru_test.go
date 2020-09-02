package acquirable

import (
	"testing"
	"time"
)

func TestRtmaRuURLS(t *testing.T) {
	dt := time.Date(2020, time.September, 1, 1, 15, 0, 0, time.UTC)
	urls := RtmaRuURLS("anl", &dt)
	urlsCorrect := []string{
		"https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtma/prod/rtma2p5_ru.20200901/rtma2p5_ru.t0100z.2dvaranl_ndfd.grb2",
		"https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtma/prod/rtma2p5_ru.20200901/rtma2p5_ru.t0115z.2dvaranl_ndfd.grb2",
		"https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtma/prod/rtma2p5_ru.20200901/rtma2p5_ru.t0130z.2dvaranl_ndfd.grb2",
		"https://nomads.ncep.noaa.gov/pub/data/nccf/com/rtma/prod/rtma2p5_ru.20200901/rtma2p5_ru.t0145z.2dvaranl_ndfd.grb2",
	}
	for idx := range urlsCorrect {
		if urlsCorrect[idx] != urls[idx] {
			t.Errorf("Bad URL!\ngot: %s\nwant: %s", urls[idx], urlsCorrect[idx])
		}
	}
}
