import React from "react";
import { connect } from "redux-bundler-react";
import debounce from "lodash.debounce";
import Navbar from "../../app-components/navbar";
import PanelGroup from "react-panelgroup";

import Map from "../../app-components/class-map";

export default connect(
  "selectMapsObject",
  "selectExploreMapKey",
  ({ mapsObject: maps, exploreMapKey: mapKey }) => {
    const map = maps[mapKey];

    const updateMapSize = debounce(() => {
      if (map) map.updateSize();
    }, 200);

    return (
      <>
        <Navbar />
        <div
          style={{
            position: "absolute",
            top: 68,
            bottom: 0,
            left: 0,
            right: 0,
          }}
        >
          <PanelGroup
            borderColor="#ccc"
            spacing={2}
            onUpdate={() => {
              updateMapSize();
            }}
          >
            <div className="min-w-full">
              <Map mapKey="exploreMap" height={"100%"} />
            </div>
            <div>
              <h1>Other Content Here</h1>
            </div>
          </PanelGroup>
        </div>
      </>
    );
  }
);
