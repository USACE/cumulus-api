# Helper functions and constants related to the HRAP Grid
# 
PROJ4 = "+proj=stere +lat_ts=60 +k_0=1 +long_0=-105 +R=6371200 +x_0=0.0 +y_0=0.0 +units=m"

# Specific to the HRAP Projection
# Given a coordinate in HRAP, calculate coordinate in Polar Stereographic
# REFERENCE: https://www.weather.gov/owp/oh_hrl_distmodel_hrap
ster_x = lambda hrap_x: hrap_x * 4762.5 - 401 * 4762.5
ster_y = lambda hrap_y: hrap_y * 4762.5 - 1601 * 4762.5
