-- adding a label to nbm-co-airtemp
UPDATE
	product
SET
	label = 'QTF',
	dss_fpart = 'NBM-QTF01'
WHERE
	id = 'd0c1d6f4-cf5d-4332-a17e-dd1757c99c94';

-- updating nbm-co-qtf-03h
UPDATE
	product
SET
	dss_fpart = 'NBM-QTF03'
WHERE
	id = 'f43cb3b8-221a-4ff0-aaa6-5937e54323b6';

-- udpating nbm-co-qtf-03h
UPDATE
	product
SET
	dss_fpart = 'NBM-QTF06'
WHERE
	id = '7e5c7acf-7d2b-4d02-a582-7ddf9b2e3700';
