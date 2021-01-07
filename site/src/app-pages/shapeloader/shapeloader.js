import React from "react";
import Admin from "../admin/admin";
import UploadButton from "./upload-button";
import ShapeTable from "./shape-table";
import { ShapeFileInfo, ShapeGeoInfo } from "./shape-info";
import Map from "../../app-components/class-map";
import { connect } from "redux-bundler-react";

const UploadButtonPanel = () => (
  <div className="shadow-2xl p-2 rounded border-2 border-black rounded-l-full flex content-center items-center bg-gray-800">
    <UploadButton>Upload</UploadButton>
  </div>
);

export default connect("selectShapefileJson", ({ shapefileJson }) => {
  return (
    <Admin>
      <div className="container mx-auto pt-4">
        <UploadButtonPanel />
        <div className="shadow-2xl mt-4 p-4 flex justify-between items-center h-400 border-2 border-gray-700 rounded">
          <div className="w-2/3">
            <ShapeFileInfo />
            <ShapeGeoInfo />
          </div>
          <div className="w-1/3 rounded-lg overflow-hidden">
            <Map mapKey="map" height={300} />
          </div>
        </div>
        <div className="mt-6 flex justify-around mt-4">
          <ShapeTable />
        </div>
      </div>
    </Admin>
  );
});
