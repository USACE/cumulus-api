-- Crooked River watershed NWP district
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)

--NWP - Crooked River
--  x_min  -2080496.6819047283
-- x_max  -1859467.910804729
-- y_min  2517089.687076909
-- y_max  2768116.934176909


--Rounded:
-- x_min  -2080497
-- x_max  -1859468
-- y_min 2517090
-- y_max  2768117


UPDATE watershed
	SET geometry = ST_GeomFromText('POLYGON ((-2080497 2768117, -1859468 2768117,-1859468 2517090, -2080497 2517090, -2080497 2768117))',5070)
WHERE id = '070204a3-66d9-471c-bd6e-ab59ea0858bb';
