package acquirable

import "time"

// NohrscSnodasUnmaskedAcquirable is a data product
type NohrscSnodasUnmaskedAcquirable struct {
	info Info
}

// URLS implements Acquirable interface
func (a *NohrscSnodasUnmaskedAcquirable) URLS() []string {
	t := time.Now()
	urlBase := "ftp://sidads.colorado.edu/DATASETS/NOAA/G02158/unmasked"
	urlFmt := "2006/01_Jan/SNODAS_unmasked_20060102.tar"

	url := urlBase + "/" + t.Format(urlFmt)

	return []string{url}
}

// Info implements Acquirable interface
func (a *NohrscSnodasUnmaskedAcquirable) Info() Info {
	return a.info
}
