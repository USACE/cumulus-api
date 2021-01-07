import React from "react";
import Navbar from "../../app-components/navbar";
import PageHeading from "../../app-components/page-heading";
import Plot from "react-plotly.js";
import AvailableProductsTabPanel from "./available-products-tab-panel";
import WatershedDetailsMap from "./ws-map";
import { connect } from "redux-bundler-react";
import Loader from "../../app-components/loader";

export default connect(
  "selectWatershedFakeByRoute",
  ({ watershedFakeByRoute: ws }) =>
    !ws ? (
      <Loader />
    ) : (
      <main className="bg-gray-200 h-full lg:h-screen">
        <Navbar />
        <div className="mx-auto max-w-screen-2xl sm:p-10">
          <PageHeading heading={ws.name} subHeading={ws.office_symbol} />

          {/* <!--first row --> */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-2 mb-3">
            <div className="order-1 min-w-full sm:min-w-0 m-3 p-3 bg-white min-h-0 rounded shadow-md">
              <AvailableProductsTabPanel />
            </div>

            <div className="order-2 inline-block col-span-2 min-w-full sm:min-w-0 m-3 p-3 bg-white rounded shadow-md">
              <WatershedDetailsMap ws={ws} />
            </div>
          </div>

          <div className="mb-3 px-3">
            <div className="flex lg:flex-row-reverse sm:text-base text-gray-600">
              {/* <div className="flex-initial inline-flex w-1/3"></div> */}
              <div className="flex-initial sm:inline-flex block">
                <span className="mr-3 p-2">Statistics Time Window:</span>
                <label htmlFor="tw_start" className="p-2">
                  Start:
                </label>
                <input
                  type="date"
                  placeholder="mm/dd/yyyy"
                  id="tw_start"
                  className="bg-transparent border-0 border-b-2 border-gray-300 focus:ring-0 focus:border-black"
                ></input>
                <label htmlFor="tw_end" className="p-2">
                  End:
                </label>
                <input
                  type="date"
                  placeholder="mm/dd/yyyy"
                  id="tw_end"
                  className="bg-transparent border-0 border-b-2 border-gray-300 focus:ring-0 focus:border-black"
                ></input>
              </div>
            </div>
          </div>

          {/* <!--second row --> */}
          <div className="grid grid-cols-1 lg:grid-cols-1 gap-2 mb-3">
            <div className="min-w-full sm:min-w-0 m-3 p-3 bg-white min-h-0 rounded shadow-md">
              <Plot
                className="w-full h-64"
                data={[
                  {
                    x: [1, 2, 3],
                    y: [2, 6, 3],
                    type: "line",
                    mode: "lines+markers",
                    marker: { color: "red" },
                  },
                  { type: "line", x: [1, 2, 3], y: [2, 5, 3] },
                ]}
                config={{ responsive: true }}
                layout={{ title: "A Fancy Plot" }}
              />
            </div>
          </div>
        </div>
      </main>
    )
);
