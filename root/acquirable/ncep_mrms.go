package acquirable

import (
	"fmt"
	"time"
)

// NcepMrmsGaugeCorrQpe01hAcquirable is NCEP MRMS GaugeCorr QPE 01H
type NcepMrmsGaugeCorrQpe01hAcquirable struct {
	info Info
}

// NCEP MRMS GaugeCorr QPE 01H
//////////////////////////////

// URLS implements Acquirable interface
func (a *NcepMrmsGaugeCorrQpe01hAcquirable) URLS() []string {
	t := time.Now().Add(time.Hour * -1)
	dateStr := t.Format("20060102-150000")
	return []string{
		fmt.Sprintf("https://mrms.ncep.noaa.gov/data/2D/GaugeCorr_QPE_01H/MRMS_GaugeCorr_QPE_01H_00.00_%s.grib2.gz", dateStr),
	}
}

// Info implements Acquirable interface
func (a *NcepMrmsGaugeCorrQpe01hAcquirable) Info() Info {
	return a.info
}
