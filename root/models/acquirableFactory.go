package models

import (
	"log"
	"time"
)

// AcquirableFactory produces the appropriate acquirable based on acquirable name
func AcquirableFactory(i *AcquirableInfo) Acquirable {
	switch {
	case i.Name == "nohrsc_snodas_unmasked":
		return &NohrscSnodasUnmaskedAcquirable{info: i}
	}

	// If we hit the end of switch/case, panic and return nil
	log.Panicf("Called for unimplemented Acquirable!!!")
	return nil
}

// NohrscSnodasUnmaskedAcquirable is a data product
type NohrscSnodasUnmaskedAcquirable struct {
	info *AcquirableInfo
}

// URLS implements Acquirable interface
func (a *NohrscSnodasUnmaskedAcquirable) URLS() []string {
	t := time.Now()
	urlFmt := "ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/unmasked/2006/01_Jan/SNODAS_unmasked_20060102.tar"
	return []string{t.Format(urlFmt)}
}

// Info implements Acquirable interface
func (a *NohrscSnodasUnmaskedAcquirable) Info() *AcquirableInfo {
	return a.info
}
