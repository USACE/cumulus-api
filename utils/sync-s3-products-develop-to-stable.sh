# CBRFC
aws s3 sync s3://cwbi-data-develop/cumulus/products/cbrfc-mpe/ s3://cwbi-data-stable/cumulus/products/cbrfc-mpe/

#HRRR Precip
aws s3 sync s3://cwbi-data-develop/cumulus/products/hrrr-total-precip/ s3://cwbi-data-stable/cumulus/products/hrrr-total-precip/

# PRISM EARLY
aws s3 sync s3://cwbi-data-develop/cumulus/products/prism-tmin-early/ s3://cwbi-data-stable/cumulus/products/prism-tmin-early/
aws s3 sync s3://cwbi-data-develop/cumulus/products/prism-tmax-early/ s3://cwbi-data-stable/cumulus/products/prism-tmax-early/
aws s3 sync s3://cwbi-data-develop/cumulus/products/prism-ppt-early/ s3://cwbi-data-stable/cumulus/products/prism-ppt-early/

# SNODAS
aws s3 sync s3://cwbi-data-develop/cumulus/products/nohrsc-snodas-swe/ s3://cwbi-data-stable/cumulus/products/nohrsc-snodas-swe/
aws s3 sync s3://cwbi-data-develop/cumulus/products/nohrsc-snodas-snowpack-average-temperature/ s3://cwbi-data-stable/cumulus/products/nohrsc-snodas-snowpack-average-temperature/
aws s3 sync s3://cwbi-data-develop/cumulus/products/nohrsc-snodas-snowmelt/ s3://cwbi-data-stable/cumulus/products/nohrsc-snodas-snowmelt/
aws s3 sync s3://cwbi-data-develop/cumulus/products/nohrsc-snodas-snowdepth/ s3://cwbi-data-stable/cumulus/products/nohrsc-snodas-snowdepth/
aws s3 sync s3://cwbi-data-develop/cumulus/products/nohrsc-snodas-coldcontent/ s3://cwbi-data-stable/cumulus/products/nohrsc-snodas-coldcontent/

# NDGD Legacy Precip/Airtemp
aws s3 sync s3://cwbi-data-develop/cumulus/products/ndgd-leia98-precip/ s3://cwbi-data-stable/cumulus/products/ndgd-leia98-precip/
aws s3 sync s3://cwbi-data-develop/cumulus/products/ndgd-ltia98-airtemp/ s3://cwbi-data-stable/cumulus/products/ndgd-ltia98-airtemp/

# RTMA Rapid Update - 15min data
aws s3 sync s3://cwbi-data-develop/cumulus/products/ncep-rtma-ru-anl-airtemp/ s3://cwbi-data-stable/cumulus/products/ncep-rtma-ru-anl-airtemp/

# MRMS v12
aws s3 sync s3://cwbi-data-develop/cumulus/products/ncep-mrms-v12-multisensor-qpe-01h-pass1/ s3://cwbi-data-stable/cumulus/products/ncep-mrms-v12-multisensor-qpe-01h-pass1/
aws s3 sync s3://cwbi-data-develop/cumulus/products/ncep-mrms-v12-multisensor-qpe-01h-pass2/ s3://cwbi-data-stable/cumulus/products/ncep-mrms-v12-multisensor-qpe-01h-pass2/

# ncep_mrms_gaugecorr_qpe_01h
aws s3 sync s3://cwbi-data-develop/cumulus/products/ncep-mrms-gaugecorr-qpe-01h/ s3://cwbi-data-stable/cumulus/products/ncep_mrms-gaugecorr-qpe-01h/

# WPC QPF
aws s3 sync s3://cwbi-data-develop/cumulus/products/wpc-qpf-2p5km/ s3://cwbi-data-stable/cumulus/products/wpc-qpf-2p5km/



########
# Notes/Command

# Verify file count
# aws s3 ls --recursive s3://cwbi-data-stable/cumulus/products/wpc-qpf-2p5km/ --summarize