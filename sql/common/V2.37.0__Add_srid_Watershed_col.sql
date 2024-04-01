-- add output_srid column to watershed table.  this column will define what output 
-- projection the grids should be in.  default as SHG EPSG 5070.
ALTER TABLE watershed ADD COLUMN output_srid INTEGER DEFAULT 5070;

--update alaska watersheds to output as EPSG 26906.
UPDATE watershed
	SET output_srid = 26906
WHERE id = 'ba17efef-1edc-4c1e-8b70-8c2d27861ee1';