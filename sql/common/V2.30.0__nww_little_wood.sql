-- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
UPDATE watershed SET geometry = ST_GeomFromText('POLYGON ((-1563072.3039047287 2329268.3385769096, -1563072.3039047287 2481928.3385769087, -1403692.3039047273 2481928.3385769087, -1403692.3039047273 2329268.3385769096, -1563072.3039047287 2329268.3385769096))',5070) WHERE id = 'abd7e8c2-69bb-4bf2-b309-478307ab523d';