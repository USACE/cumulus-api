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

// PrismEarlyURL returns the standard Prism download URL
// The URLs for different parameters are the same, except for parameter short codes
func PrismEarlyURL(p string, t *time.Time) string {
	year, ymd := t.Format("2006"), t.Format("20060102")
	return fmt.Sprintf("ftp://prism.nacse.org/daily/%s/%s/PRISM_%s_early_4kmD2_%s_bil.zip", p, year, p, ymd)
}

// PRISM PPT EARLY
///////////////////////////////////////

// URLS implements Acquirable interface
func (a *PrismPptEarlyAcquirable) URLS() []string {
	t := time.Now().AddDate(0, 0, -1)
	return []string{
		PrismEarlyURL("ppt", &t),
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
		t.Format(PrismEarlyURL("tmax", &t)),
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
		t.Format(PrismEarlyURL("tmin", &t)),
	}
}

// Info implements Acquirable interface
func (a *PrismTminEarlyAcquirable) Info() Info {
	return a.info
}
