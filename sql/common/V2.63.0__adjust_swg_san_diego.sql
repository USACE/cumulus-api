-- update san diego creek watershed
-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed
SET geometry = ST_GeomFromText('Polygon ((
                        -266955 561275,
                        -193507 561275,
                        -193507 513001,
                        -266955 513001,
                        -266955 561275))',
                                5070)
                WHERE slug = 'san-diego-creek';