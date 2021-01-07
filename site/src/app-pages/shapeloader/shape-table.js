import React from "react";
import { connect } from "redux-bundler-react";

export default connect(
  "selectShapefileJsonFeatures",
  ({ shapefileJsonFeatures: features }) => {
    //   Assume all features have the same properties
    const headers = !features.length ? [] : Object.keys(features[0].properties);

    return (
      <table className="table-auto">
        <thead>
          <tr>
            {headers.map((h, idx) => (
              <th key={idx} className="px-4 py-2">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {features.map((f, idx) => (
            <tr className="border px-4 py-2" key={idx}>
              {headers.map((h, idx) => (
                <td key={idx}>{f.properties[h]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  }
);
