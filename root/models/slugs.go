package models

import (
	"fmt"
	"strconv"
	"strings"

	"github.com/gosimple/slug"
	"github.com/jmoiron/sqlx"
)

// NextUniqueSlug returns the next available slug given a table, slug field, and un-slugified string
func NextUniqueSlug(db *sqlx.DB, table string, field string, inString string) (string, error) {
	// Slugify string; this is the first choice for a slug if it's not already taken
	slugTry := slug.Make(inString)

	// Find what's already taken by this name as-is or same but suffixed by xxx-1, xxx-2, etc.
	sql := fmt.Sprintf(
		`SELECT %s FROM %s WHERE %s ~ ($1||'(?:-[0-9]+)?$') ORDER BY %s DESC`,
		field, table, field, field,
	)
	ss := make([]string, 0)
	if err := db.Select(&ss, sql, slugTry); err != nil {
		return "", err
	}

	// If the last entry based on sort DESC is not slugTry
	// we know the slug is free. Regex gets dicey when a slug like
	// "test-watershed-1" exists, "test-watershed" does not, and you
	// run this method on inString for "test-watershed".
	if len(ss) == 0 || ss[len(ss)-1] != slugTry {
		return slugTry, nil
	}
	// If slugTry already taken; add "-1" to the end
	if len(ss) == 1 {
		return fmt.Sprintf("%s-1", slugTry), nil
	}
	// If there are many of these slugs already (i.e. myslug, myslug-1, myslug-2, etc.)
	// iterate to find the next available integer to tag on the end
	largest := 1
	pLargest := &largest
	for idx := range ss[:len(ss)-1] {
		parts := strings.Split(ss[idx], "-")
		i, err := strconv.Atoi(parts[len(parts)-1])
		if err != nil {
			return "", err
		}
		if i > *pLargest {
			*pLargest = i
		}
	}
	return fmt.Sprintf("%s-%d", slugTry, *pLargest+1), nil
}
