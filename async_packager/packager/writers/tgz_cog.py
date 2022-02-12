import json
import os
from osgeo import gdal

import config as CONFIG

# NOTE: SCAFFOLD; WORK IN PROGRESS
def writer(outfile, extent, items, callback, cellsize=2000, dst_srs="EPSG:5070"):

    item_length, contents = len(items), []
    for idx, item in enumerate(items):
        try:
            # Update progress at predefined interval
            if idx % CONFIG.PACKAGER_UPDATE_INTERVAL == 0 or idx == item_length-1:
                callback(idx)
            
            filename = f'{item["dss_fpart"]}_{item["dss_cpart"]}_{item["dss_dpart"]}_{item["dss_epart"]}.tif'        
            ds = gdal.Warp(
                f'/vsitar/{filename}',
                f'/vsis3_streaming/{item["bucket"]}/{item["key"]}',
                dstSRS=dst_srs,
                outputType=gdal.GDT_Float64,
                outputBounds=extent['bbox'],
                resampleAlg="bilinear",
                targetAlignedPixels=True,
                xRes=cellsize,
                yRes=cellsize,
            )
            item['filename'] = filename
            contents.append(item)
        except:
            print(f'Unable to process: {item["bucket"]}/{item["key"]}')
        finally:
            ds = None
    
    if len(contents) > 0:
        # JSON Dump Contents to an index.json file in tar.gz
        print(json.dumps(contents))
        
    return os.path.abspath(outfile)
