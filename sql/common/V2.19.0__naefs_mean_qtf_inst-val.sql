-- update the temporal_duration for NAEFS MEAN QTF to represent a DSS INST-VAL

UPDATE
	product
SET
	temporal_duration = 0,
	dss_datatype_id = 'b1433fa7-645f-4e3c-b560-29cba59e80c6'
WHERE
	id = '60f16079-7495-47ab-aa68-36cd6a17fce0'
