import React from "react";
import { connect } from "redux-bundler-react";
import Loader from "../../app-components/loader";

export default connect(
  "selectWatershedItemsArray",
  ({ watershedItemsArray: watersheds }) =>
    !watersheds || !watersheds.length ? (
      <Loader />
    ) : (
      <div>
        {watersheds.map((w, idx) => (
          <div key={idx}>
            <a href={`/ws/${w.slug}`}>{w.name}</a>
          </div>
        ))}
      </div>
    )
);
