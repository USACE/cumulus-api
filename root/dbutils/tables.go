package dbutils

import (
	"database/sql"
	"fmt"
)

// Domains
func createTableExample(db *sql.DB) {
	sql := `
	CREATE TABLE IF NOT EXISTS public.example (
		id UUID PRIMARY KEY NOT NULL DEFAULT uuid_generate_v4(),
		name VARCHAR(120) UNIQUE NOT NULL
	);
	`
	_, err := db.Exec(sql)
	if err != nil {
		panic(err)
	}
}

// CreateTables creates database tables and views if they do not exist
func CreateTables(db *sql.DB) {
	fmt.Println("CreateTables Not Implemented")
}
