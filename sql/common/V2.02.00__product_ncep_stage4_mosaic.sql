INSERT INTO acquirable (id, name, slug) VALUES   
    ('29b1e90b-3f8c-484f-a7fa-7055aec4d5b8', 'ncep-stage4-mosaic-01h', 'ncep-stage4-mosaic-01h');

INSERT INTO suite (id, name, slug, description) VALUES
    ('96d0250c-bf16-447f-8ccc-b15134c1ab99', 'National Centers for Environmental Predictions (NCEP)', 'ncep', 'The National Centers for Environmental Prediction (NCEP) determine data requirements, optimum data processing techniques, and suitable presentation methods for predictions and products distributed to users of climatic, hydrologic, meteorological, space weather, and oceanographic information.');

INSERT INTO product (id,slug,"label",temporal_duration,temporal_resolution,dss_fpart,parameter_id,description,unit_id,deleted,suite_id) VALUES
    ('16d4c494-63e6-4d33-b2da-7be065a6776b','ncep-stage4-mosaic-01h','STAGE4 MOSAIC QPE',3600,3600,'NCEP-STAGE4','eb82d661-afe6-436a-b0df-2ab0b478a1af','Precipitation estimates by the 12 River Forecast Centers (RFCs) in CONUS','e245d39f-3209-4e58-bfb7-4eae94b3f8dd',false,'96d0250c-bf16-447f-8ccc-b15134c1ab99');
