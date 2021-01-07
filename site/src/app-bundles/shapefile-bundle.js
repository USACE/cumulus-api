import shp from "shpjs";
// import dissolve from "@turf/dissolve";
import { bbox, flatten, simplify, truncate } from "@turf/turf";
import proj4 from "proj4";

import { createSelector } from "redux-bundler";

const readFileAsync = (file) => {
  return new Promise((resolve, reject) => {
    let reader = new FileReader();

    reader.onload = () => {
      resolve(reader.result);
    };

    reader.onerror = reject;

    reader.readAsArrayBuffer(file);
  });
};

const shapefileBundle = {
  name: "shapefile",
  getReducer: () => {
    const initialData = {
      zip: null,
      json: null,
      bbox: null,
      crsSupported: [
        [
          "EPSG:5070",
          "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=23 +lon_0=-96 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=1,1,-1,0,0,0,0 +units=m +no_defs",
        ],
        ["EPSG:4326", "+proj=longlat +datum=WGS84 +no_defs"],
      ],
      cellSize: 2000,
      cellBuffer: 2,
      _shouldParseJson: false,
      _isParsing: false,
      _shouldDissolve: false,
      _isDissolving: false,
    };

    return (state = initialData, { type, payload }) => {
      switch (type) {
        case "SHAPEFILE_QUEUE_ZIP":
        case "SHAPEFILE_PARSE_JSON_START":
        case "SHAPEFILE_PARSE_JSON_FINISH":
        case "SHAPEFILE_DISSOLVE_START":
        case "SHAPEFILE_DISSOLVE_FINISH":
          return Object.assign({}, state, payload);
        default:
          return state;
      }
    };
  },
  doShapefileQueueZip: (zip) => ({ dispatch }) => {
    dispatch({
      type: "SHAPEFILE_QUEUE_ZIP",
      payload: { zip: zip, _shouldParseJson: true },
    });
  },
  doShapefileParseJson: () => async ({ dispatch, store }) => {
    dispatch({
      type: "SHAPEFILE_PARSE_JSON_START",
      payload: { _isParsing: true, _shouldParseJson: false },
    });

    const zip = store.selectShapefileZip();
    const file = await readFileAsync(zip);
    shp(file).then((json) => {
      dispatch({
        type: "SHAPEFILE_PARSE_JSON_FINISH",
        payload: {
          _isParsing: false,
          _shouldDissolve: true,
          json: json,
        },
      });
    });
  },
  doShapefileDissolve: () => ({ store, dispatch }) => {
    dispatch({
      type: "SHAPEFILE_DISSOLVE_START",
      payload: { _isDissolving: true, _shouldDissolve: false },
    });

    const fcRaw = store.selectShapefileJson();
    // @todo do not purge multipolygons blindly
    const fc = flatten(fcRaw);
    const tt = truncate(fc, { precision: 6, coordinates: 2 });
    const ss = simplify(tt, { tolerance: 1 });
    const bb = bbox(ss);

    dispatch({
      type: "SHAPEFILE_DISSOLVE_FINISH",
      payload: { _isDissolving: false, bbox: bb, dissolve: ss },
    });
  },
  selectShapefileZip: (state) => state.shapefile.zip,
  selectShapefileJson: (state) => state.shapefile.json,
  selectShapefileJsonFeatures: createSelector("selectShapefileJson", (json) => {
    console.log(json);
    return json === null ? [] : json.features;
  }),
  selectShapefileBbox: (state) => state.shapefile.bbox,
  selectShapefileBbox5070: createSelector(
    "selectShapefileBbox",
    "selectShapefileCrsSupported",
    "selectShapefileCellSize",
    "selectShapefileCellBuffer",
    (bbox, crsSupported, cellSize, cellBuffer) => {
      const roundDown = (val) =>
        Math.floor(val / cellSize - cellBuffer) * cellSize;

      const roundUp = (val) =>
        Math.ceil(val / cellSize + cellBuffer) * cellSize;

      if (bbox === null) {
        return null;
      }

      proj4.defs(crsSupported);
      const [x_min, y_min] = proj4("EPSG:4326", "EPSG:5070", [
        bbox[0],
        bbox[1],
      ]);
      const [x_max, y_max] = proj4("EPSG:4326", "EPSG:5070", [
        bbox[2],
        bbox[3],
      ]);
      return [
        roundDown(x_min),
        roundDown(y_min),
        roundUp(x_max),
        roundUp(y_max),
      ];
    }
  ),
  selectShapefileCellSize: (state) => state.shapefile.cellSize,
  selectShapefileCellBuffer: (state) => state.shapefile.cellBuffer,
  selectShapefileJsonDissolve: (state) => state.shapefile.dissolve,
  selectShapefileCrsSupported: (state) => state.shapefile.crsSupported,
  reactShapefileShouldParseJson: (state) => {
    if (state.shapefile._shouldParseJson)
      return { actionCreator: "doShapefileParseJson" };
  },
  reactShapefileShouldDissolve: (state) => {
    if (state.shapefile._shouldDissolve)
      return { actionCreator: "doShapefileDissolve" };
  },
};

export default shapefileBundle;
