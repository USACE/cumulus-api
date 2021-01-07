import React from "react";
import Map from "../../app-components/class-map";

const WatershedDetailsMap = ({ ws }) => {
  return (
    <div>
      <span className="font-bold text-gray-600 text-md text-secondary uppercase tracking-wider mr-4">
        Watershed Map
      </span>
      <span className="font-bold text-gray-500 text-sm lg:text-md text-secondary mr-4 xl:float-right">
        SHG Extents (EPSG:5070): x_min: {ws.x_min}, y_min: {ws.y_min}, x_max:{" "}
        {ws.x_max}, y_max: {ws.y_max}
      </span>

      <div className="h-96 mt-3 bg-gray-500">
        <Map mapKey="exploreMap" height={"100%"} />
      </div>
    </div>
  );
};

export default WatershedDetailsMap;
