package acquirable

import (
	"fmt"
	"time"
)

// PrismPptEarlyAcquirable is Prism Precipitation
type PrismPptEarlyAcquirable struct {
	info Info
}

// PrismTmaxEarlyAcquirable is Prism Maximum Temperature
type PrismTmaxEarlyAcquirable struct {
	info Info
}

// PrismTminEarlyAcquirable is Prism Maximum Temperature
type PrismTminEarlyAcquirable struct {
	info Info
}

// PrismEarlyURLFormat returns the standard Prism download URL
// The URLs for different parameters are the same, except for parameter short codes
func PrismEarlyURLFormat(p string) string {
	return fmt.Sprintf("ftp://prism.nacse.org/daily/%s/2006/PRISM_%s_early_4kmD2_20060102_bil.zip", p, p)
}

// PRISM PPT EARLY
///////////////////////////////////////

// URLS implements Acquirable interface
func (a *PrismPptEarlyAcquirable) URLS() []string {
	t := time.Now().AddDate(0, 0, -1)
	return []string{
		t.Format(PrismEarlyURLFormat("ppt")),
	}
}

// Info implements Acquirable interface
func (a *PrismPptEarlyAcquirable) Info() Info {
	return a.info
}

// PRISM TMAX EARLY
///////////////////////////////////////

// URLS implements Acquirable interface
func (a *PrismTmaxEarlyAcquirable) URLS() []string {
	t := time.Now().AddDate(0, 0, -1)
	return []string{
		t.Format(PrismEarlyURLFormat("tmax")),
	}
}

// Info implements Acquirable interface
func (a *PrismTmaxEarlyAcquirable) Info() Info {
	return a.info
}

// PRISM TMIN EARLY
///////////////////////////////////////

// URLS implements Acquirable interface
func (a *PrismTminEarlyAcquirable) URLS() []string {
	t := time.Now().AddDate(0, 0, -1)
	return []string{
		t.Format(PrismEarlyURLFormat("tmin")),
	}
}

// Info implements Acquirable interface
func (a *PrismTminEarlyAcquirable) Info() Info {
	return a.info
}
