-- Add MVM (Memphis District) whole district watershed

-- extent to polygon reference order - simple 4 point extents
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
INSERT INTO watershed (id,slug,"name",geometry,office_id) VALUES
	 ('150f6090-2d50-4dea-96dd-deadd7148fb4','memphis-district','Memphis District',ST_GeomFromText('POLYGON ((180000 1662000, 748000 1662000, 748000 1104000, 180000 1104000, 180000 1662000))',5070),'8fc88b15-9cd4-4e86-8b8c-6d956926010b');