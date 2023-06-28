import json
import math

buffer, cellsize = 0, 2000
round_down = lambda val: int((math.floor(val / cellsize) * cellsize) - buffer)
round_up = lambda val: int((math.ceil(val / cellsize) * cellsize) + buffer)

_json = """{
"type": "FeatureCollection",
"name": "rfc",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::5070" } },
"bbox": [ -2356057.872395, 209814.622771785, 2258191.54104844, 3505169.15998809 ],                                                 
"features": [
{ "type": "Feature", "properties": { "OBJECTID": 2, "SITE_ID": "KRF", "STATE": "MO", "RFC_NAME": "Missouri Basin", "RFC_CITY": "Kansas City\/Pleasant Hill", "BASIN_ID": "MBRFC" }, "bbox": [ -1389593, 1556204, 483276, 3043875 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ -1389593, 1556204 ], [ 483276, 1556204 ], [ 483276, 3043875 ], [ -1389593, 3043875 ], [ -1389593, 1556204 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 3, "SITE_ID": "STR", "STATE": "UT", "RFC_NAME": "Colorado Basin", "RFC_CITY": "Salt Lake City", "BASIN_ID": "CBRFC" }, "bbox": [ -1774279, 999789, -811701, 2357426 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ -1774279, 999789 ], [ -811701, 999789 ], [ -811701, 2357426 ], [ -1774279, 2357426 ], [ -1774279, 999789 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 4, "SITE_ID": "TUA", "STATE": "OK", "RFC_NAME": "Arkansas-Red Basin", "RFC_CITY": "Tulsa", "BASIN_ID": "ABRFC" }, "bbox": [ -907431, 1147930, 367713, 1866333 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ -907431, 1147930 ], [ 367713, 1147930 ], [ 367713, 1866333 ], [ -907431, 1866333 ], [ -907431, 1147930 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 5, "SITE_ID": "RSA", "STATE": "CA", "RFC_NAME": "California-Nevada", "RFC_CITY": "Sacramento", "BASIN_ID": "CNRFC" }, "bbox": [ -2356058, 1243480, -1518404, 2540457 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ -2356058, 1243480 ], [ -1518404, 1243480 ], [ -1518404, 2540457 ], [ -2356058, 2540457 ], [ -2356058, 1243480 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 6, "SITE_ID": "ORN", "STATE": "LA", "RFC_NAME": "Lower Mississippi", "RFC_CITY": "New Orleans\/Baton Rouge", "BASIN_ID": "LMRFC" }, "bbox": [ -23139, 673055, 1293858, 1702397 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ -23139, 673055 ], [ 1293858, 673055 ], [ 1293858, 1702397 ], [ -23139, 1702397 ], [ -23139, 673055 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 7, "SITE_ID": "RHA", "STATE": "PA", "RFC_NAME": "Middle Atlantic", "RFC_CITY": "Central Pennsylvania", "BASIN_ID": "MARFC" }, "bbox": [ 1350832, 1687761, 1843609, 2404393 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ 1350832, 1687761 ], [ 1843609, 1687761 ], [ 1843609, 2404393 ], [ 1350832, 2404393 ], [ 1350832, 1687761 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 8, "SITE_ID": "MSR", "STATE": "MN", "RFC_NAME": "North Central", "RFC_CITY": "Minneapolis", "BASIN_ID": "NCRFC" }, "bbox": [ -650499, 1616600, 1097654, 3052061 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ -650499, 1616600 ], [ 1097654, 1616600 ], [ 1097654, 3052061 ], [ -650499, 3052061 ], [ -650499, 1616600 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 9, "SITE_ID": "TAR", "STATE": "MA", "RFC_NAME": "Northeast", "RFC_CITY": "Boston", "BASIN_ID": "NERFC" }, "bbox": [ 1361036, 2161958, 2258192, 3040497 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ 1361036, 2161958 ], [ 2258192, 2161958 ], [ 2258192, 3040497 ], [ 1361036, 3040497 ], [ 1361036, 2161958 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 10, "SITE_ID": "PTR", "STATE": "OR", "RFC_NAME": "Northwest", "RFC_CITY": "Portland", "BASIN_ID": "NWRFC" }, "bbox": [ -2294670, 2191666, -1103294, 3505169 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ -2294670, 2191666 ], [ -1103294, 2191666 ], [ -1103294, 3505169 ], [ -2294670, 3505169 ], [ -2294670, 2191666 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 11, "SITE_ID": "TIR", "STATE": "OH", "RFC_NAME": "Ohio", "RFC_CITY": "Cincinatti", "BASIN_ID": "OHRFC" }, "bbox": [ 610718, 1413236, 1488217, 2294358 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ 610718, 1413236 ], [ 1488217, 1413236 ], [ 1488217, 2294358 ], [ 610718, 2294358 ], [ 610718, 1413236 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 12, "SITE_ID": "ALR", "STATE": "GA", "RFC_NAME": "Southeast", "RFC_CITY": "Atlanta", "BASIN_ID": "SERFC" }, "bbox": [ 630164, 273886, 1833437, 1740464 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ 630164, 273886 ], [ 1833437, 273886 ], [ 1833437, 1740464 ], [ 630164, 1740464 ], [ 630164, 273886 ] ] ] } },
{ "type": "Feature", "properties": { "OBJECTID": 13, "SITE_ID": "FWR", "STATE": "TX", "RFC_NAME": "West Gulf", "RFC_CITY": "Dallas\/Fort Worth", "BASIN_ID": "WGRFC" }, "bbox": [ -1205734, 209815, 270829, 1759952 ], "geometry": { "type": "Polygon", "coordinates": [ [ [ -1205734, 209815 ], [ 270829, 209815 ], [ 270829, 1759952 ], [ -1205734, 1759952 ], [ -1205734, 209815 ] ] ] } }
]
}"""

rfcs = json.loads(_json)

for f in rfcs["features"]:

    xmin, ymin, xmax, ymax = (
        round_down(f["bbox"][0]),
        round_down(f["bbox"][1]),
        round_up(f["bbox"][2]),
        round_up(f["bbox"][3]),
    )

    # -- xmin,ymax (top left), xmax ymax (top right), xmax ymin (bottom right), xmin ymin (bottom left), xmin ymax (top left again)
    print(
        "'{}',ST_GeomFromText('POLYGON (({} {}, {} {}, {} {}, {} {}, {} {}))', 5070)".format(
            f["properties"]["BASIN_ID"],
            xmin,
            ymax,
            xmax,
            ymax,
            xmax,
            ymin,
            xmin,
            ymin,
            xmin,
            ymax,
        )
    )
