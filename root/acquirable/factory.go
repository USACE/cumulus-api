package acquirable

import (
	"errors"

	"github.com/google/uuid"
)

// Acquirable interface
type Acquirable interface {
	Info() Info
	URLS() []string
}

// Info stores common data for an Acquirable
type Info struct {
	ID       uuid.UUID `json:"id"`
	Name     string    `json:"name"`
	Schedule string    `json:"schedule"`
}

// AcquisitionAttempt is a data retrieval request
type AcquisitionAttempt struct {
	ID       uuid.UUID `json:"id"`
	Datetime string    `json:"datetime"`
}

// Acquisition is the acquisition of an acquirable
type Acquisition struct {
	ID            uuid.UUID `json:"id"`
	AcquisitionID uuid.UUID `json:"acquisition_id" db:"acquisition_id"`
	AcquirableID  uuid.UUID `json:"acquirable_id" db:"acquirable_id"`
}

// Factory produces the appropriate acquirable based on acquirable name
func Factory(i Info) (Acquirable, error) {
	switch i.Name {
	case "nohrsc_snodas_unmasked":
		return &NohrscSnodasUnmaskedAcquirable{info: i}, nil
	case "prism_ppt_early":
		return &PrismPptEarlyAcquirable{info: i}, nil
	case "prism_tmax_early":
		return &PrismTmaxEarlyAcquirable{info: i}, nil
	case "prism_tmin_early":
		return &PrismTminEarlyAcquirable{info: i}, nil
	case "ncep_rtma_ru_anl":
		return &NcepRtmaRuAnlAcquirable{info: i}, nil
	case "ncep_rtma_ru_ges":
		return &NcepRtmaRuGesAcquirable{info: i}, nil
	case "ncep_mrms_gaugecorr_qpe_01h":
		return &NcepMrmsGaugeCorrQpe01hAcquirable{info: i}, nil
	case "ncep_mrms_v12_MultiSensor_QPE_01H_Pass1":
		return &NcepMrmsV12MultiSensorQPE01HPass1Acquirable{info: i}, nil
	case "ncep_mrms_v12_MultiSensor_QPE_01H_Pass2":
		return &NcepMrmsV12MultiSensorQPE01HPass2Acquirable{info: i}, nil
	}
	return nil, errors.New("acquirable not implemented")
}
