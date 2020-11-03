// ('ncep_mrms_v12_MultiSensor_QPE_01H_Pass1', '5 * * * *'),
// ('ncep_mrms_v12_MultiSensor_QPE_01H_Pass2', '5 * * * *');

package acquirable

import (
	"fmt"
	"time"
)

// NcepMrmsV12MultiSensorQPE01HPass1Acquirable is NCEP MRMS GaugeCorr QPE 01H
type NcepMrmsV12MultiSensorQPE01HPass1Acquirable struct {
	info Info
}

// URLS implements Acquirable interface
func (a *NcepMrmsV12MultiSensorQPE01HPass1Acquirable) URLS() []string {
	t := time.Now().Add(time.Hour * -1)
	dateStr := t.Format("20060102-150000")
	return []string{
		fmt.Sprintf("https://mrms.ncep.noaa.gov/data/2D/MultiSensor_QPE_01H_Pass1/MRMS_MultiSensor_QPE_01H_Pass1_00.00_%s.grib2.gz", dateStr),
	}
}

// Info implements Acquirable interface
func (a *NcepMrmsV12MultiSensorQPE01HPass1Acquirable) Info() Info {
	return a.info
}

// NcepMrmsV12MultiSensorQPE01HPass2Acquirable is NCEP MRMS GaugeCorr QPE 01H
type NcepMrmsV12MultiSensorQPE01HPass2Acquirable struct {
	info Info
}

// URLS implements Acquirable interface
func (a *NcepMrmsV12MultiSensorQPE01HPass2Acquirable) URLS() []string {
	t := time.Now().Add(time.Hour * -2)
	dateStr := t.Format("20060102-150000")
	return []string{
		fmt.Sprintf("https://mrms.ncep.noaa.gov/data/2D/MultiSensor_QPE_01H_Pass2/MRMS_MultiSensor_QPE_01H_Pass2_00.00_%s.grib2.gz", dateStr),
	}
}

// Info implements Acquirable interface
func (a *NcepMrmsV12MultiSensorQPE01HPass2Acquirable) Info() Info {
	return a.info
}
