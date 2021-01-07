import React from "react";
import Navbar from "../../app-components/navbar";
import PageHeading from "../../app-components/page-heading";
import Download from "../../app-components/download";
import { connect } from "redux-bundler-react";

export default connect("selectAuthUsername", (props) => {
  return (
    <main className="bg-gray-200 h-full lg:h-screen">
      <Navbar />
      <div className="mx-auto max-w-screen-2xl sm:p-10">
        <PageHeading
          heading={"Cumulus Downloads"}
          subHeading={"Meteorology With Simple Data Access"}
        />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="order-1 min-w-full sm:min-w-0 m-3 p-3 bg-white min-h-0 rounded shadow-md border-l-8 border-gray-400">
            <Download />
          </div>
          <div className="order-2 min-w-full sm:min-w-0 m-3 p-3 bg-gray-100 min-h-0 rounded shadow-md border-l-8 border-gray-200">
            <h3 className="mb-3 text-2xl">Download Info:</h3>
            <div className="block mb-2 w-full p-1 mt-5 font-bold text-gray-600 text-sm text-secondary uppercase tracking-wider">
              Request Payload
            </div>
            <textarea rows="5" cols="60" className="w-full">
              {JSON.stringify(
                {
                  datetime_start: "2020-11-18T06:00:00Z",
                  datetime_end: "2020-12-02T06:00:00Z",
                  basin_id: "f019ffec-e9d3-48e6-ab74-eaa8fd8065e0",
                  product_id: ["e4fdadc7-5532-4910-9ed7-3c3690305d86"],
                },
                null,
                2
              )}
            </textarea>
            <div className="block mb-2 w-full p-1 mt-5 font-bold text-gray-600 text-sm text-secondary uppercase tracking-wider">
              Download Status:
            </div>
            <div className="relative pt-1">
              <div className="flex mb-2 items-center justify-between">
                <div>
                  <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-green-600 bg-green-200">
                    Task in progress
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-semibold inline-block text-green-600">
                    50%
                  </span>
                </div>
              </div>
              <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
                <div
                  style={{ width: "50%" }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
                ></div>
              </div>
            </div>
            <button
              disabled
              className="bg-gray-300 /*hover:bg-gray-400*/ cursor-not-allowed opacity-50 text-gray-800 font-bold py-2 px-4 rounded inline-flex items-center"
            >
              <svg
                className="fill-current w-4 h-4 mr-2"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
              >
                <path d="M13 8V2H7v6H2l8 8 8-8h-5zM0 18h20v2H0v-2z" />
              </svg>
              <span>Download</span>
            </button>
          </div>
        </div>
      </div>
    </main>
  );
});
