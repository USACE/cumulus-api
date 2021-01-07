import React from "react";
import Navbar from "../../app-components/navbar";
import { connect } from "redux-bundler-react";
import CalendarHeatmap from "react-calendar-heatmap";
import "react-calendar-heatmap/dist/styles.css";
import ReactTooltip from "react-tooltip";
import moment from "moment";

import Map from "../../app-components/class-map";

import Loader from "../../app-components/loader";

const colorClassBinary = (value) => {
  if (!value || !value.count) {
    return "fill-current text-gray-300";
  } else {
    return "fill-current text-green-400";
  }
};

const colorClassHourly = (value) => {
  const color = ({ count }) =>
    count === 24
      ? "text-green-500"
      : count < 24 && count > 20
      ? "text-green-300"
      : count < 20 && count > 0
      ? "text-green-200"
      : "text-gray-200";

  return `fill-current ${value ? color(value) : "text-gray-200"}`;
};

const AvailabilityCalendar = ({ year, dates, classForValue }) => {
  return (
    <div className="flex flex-row justify-between items-center p-2 m-4">
      <div className="mx-2">
        <h1 className="text-md mb-2">{`WY${year}`}</h1>
      </div>
      <div className="flex-grow">
        <CalendarHeatmap
          startDate={new Date(`${year - 1}-10-01`)}
          endDate={new Date(`${year}-09-30`)}
          values={dates}
          classForValue={classForValue}
          tooltipDataAttrs={(value) =>
            value &&
            value.date && {
              "data-tip": `${moment.utc(value.date).format("YYYY-MM-DD")}: ${
                value.count
              } Grids`,
            }
          }
        />
        <ReactTooltip />
      </div>
    </div>
  );
};

export default connect(
  "selectProductByRoute",
  "selectProductYearsByRoute",
  "selectProductavailabilityByRoute",
  "selectProductavailabilityIsLoading",
  ({
    productByRoute: product,
    productYearsByRoute: productYears,
    productavailabilityByRoute: productAvailability,
    productavailabilityIsLoading: isLoading,
  }) => {
    // Color Ramp Depends on Hourly vs. Daily temporal_resolution
    const classForValue = (resolution) => {
      return parseInt(resolution) === 3600
        ? colorClassHourly
        : colorClassBinary;
    };
    return (
      product && (
        <main>
          <Navbar />
          <div className="container mx-auto">
            <h1 className="mt-12 text-3xl font-sans">{product.name}</h1>
            <hr className="mt-4" />
            <div className="mt-6 flex flex-row">
              <div className="w-2/3">
                <div className="border border-2 rounded-lg m-2 p-2">
                  <h1 className="font-sans text-lg">Availability Details</h1>
                  <hr />
                  {isLoading || !productAvailability ? (
                    <Loader opt={"dissolve-cube"} color={"#9ae6b4"} />
                  ) : (
                    productYears.map((year, idx) => (
                      <AvailabilityCalendar
                        key={idx}
                        year={year}
                        dates={productAvailability.date_counts}
                        classForValue={classForValue(
                          product.temporal_resolution
                        )}
                      />
                    ))
                  )}
                </div>
              </div>
              <div className="w-1/3">
                {/* MAP */}
                <div className="mb-8 border border-2 rounded-lg m-2 overflow-hidden">
                  <Map
                    mapKey={"productDetailMap"}
                    height={300}
                    options={{
                      center: [-98.0, 37.0],
                      zoom: 2,
                    }}
                  />
                </div>

                {/* METADATA  */}
                <div className="border border-2 rounded-lg m-2 p-2">
                  <h1 className="p-2 text-lg">Metadata</h1>
                  <hr />
                  <table className="table-auto">
                    <thead>
                      <tr>
                        <th className="px-4 py-2"></th>
                        <th className="px-4 py-2"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.keys(product).map((k, idx) => (
                        <tr>
                          <td className="px-4 py-2 font-light">{k}</td>
                          <td className="px-4 py-2 font-light text-md">
                            {product[k]}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </main>
      )
    );
  }
);
