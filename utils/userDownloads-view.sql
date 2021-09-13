select 
d.id, 
d.datetime_start,
d.datetime_end,
d.datetime_end-d.datetime_start as time_window,
d.processing_start,
d.processing_end-d.processing_start as processing_time,
d.progress,
ds.name as status_name,
w.name as watershed_name,
o.name as watershed_office,
file,
dp.product_id,
p.username
from cumulus.download d
join cumulus.download_status ds on ds.id=d.status_id
join cumulus.watershed w on w.id=d.watershed_id 
join cumulus.office o on o.id=w.office_id
left join cumulus.profile p on p.id=d.profile_id
JOIN (SELECT array_agg(download_product.product_id) AS product_id,
	download_product.download_id
	FROM cumulus.download_product
	GROUP BY download_product.download_id) dp ON d.id = dp.download_id
order by processing_start desc