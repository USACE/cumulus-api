-- Crooked River watershed NWP district
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)

--NWP - Crooked River
-- x_min  -6825762.86388243
-- x_max  -6100604.304031842
-- y_min  8258151.748351492
-- y_max  9081730.308212077
--Rounded:
-- x_min  -6825763
-- x_max  -6100605
-- y_min  8258152
-- y_max  9081731


UPDATE watershed
	SET geometry = ST_GeomFromText('POLYGON ((-7245681 5375027, -6825665 5375027, -6825665 5057730, -7245681 5057730, -7245681 5375027))',5070)
WHERE id = '070204a3-66d9-471c-bd6e-ab59ea0858bb';
