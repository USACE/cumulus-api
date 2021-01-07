import React from "react";
import { connect } from "redux-bundler-react";

const ShapeFileInfo = connect("selectShapefileZip", ({ shapefileZip: zip }) => (
  <div>
    <h1>
      {zip === null
        ? ""
        : `Filename: ${zip.name}; Filesize: ${
            zip.size * 0.000001
          } MB; Last Modified: ${zip.lastModifiedDate}`}
    </h1>
  </div>
));

const ShapeGeoInfo = connect(
  "selectShapefileBbox",
  "selectShapefileBbox5070",
  ({ shapefileBbox: bbox, shapefileBbox5070: bbox5070 }) =>
    bbox !== null && (
      <div className="flex justify-around">
        <div>
          <h1 className="underline">Coordinates Native</h1>
          <h1>Xmin: {bbox[0]}</h1>
          <h1>Ymin: {bbox[1]}</h1>
          <h1>Xmax: {bbox[2]}</h1>
          <h1>Ymax: {bbox[3]}</h1>
        </div>
        <div>
          <h1 className="underline">Coordinates SHG</h1>
          <h1>Xmin: {bbox5070[0]}</h1>
          <h1>Ymin: {bbox5070[1]}</h1>
          <h1>Xmax: {bbox5070[2]}</h1>
          <h1>Ymax: {bbox5070[3]}</h1>
        </div>
      </div>
    )
);

// const GeoInfo =
export { ShapeFileInfo, ShapeGeoInfo };
