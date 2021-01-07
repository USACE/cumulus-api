import React from "react";
import Navbar from "../../app-components/navbar";
import PageHeading from "../../app-components/page-heading";
import MyWatersheds from "./my-watersheds/my-watersheds";
import Downloads from "./downloads/downloads";

function dashboard() {
  return (
    <>
      <main className="bg-gray-200 h-full lg:h-screen">
        <Navbar />
        <div className="mx-auto max-w-screen-2xl sm:p-10">
          {/* <div className="mb-3 pl-3">
            <h2 className="text-4xl font-medium font-bold text-gray-800 m-0">
              Cumulus Dashboard
            </h2>
            <div className="text-secondary text-gray-600 font-bold tracking-tight">
              Meteorology With Simple Data Access
            </div> 
          </div>*/}
          <PageHeading
            heading={"Cumulus Dashboard"}
            subHeading="Meteorology With Simple Data Access"
          />

          {/* <!--top row --> */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-3">
            <a href="/catalog">
              <div className="order-1 min-w-full sm:min-w-0 m-3 p-3 bg-white min-h-0 rounded shadow-md border-l-8 border-green-600 hover:text-green-700">
                <div className="text-5xl">19</div>
                <span className="font-bold text-gray-600 text-md text-secondary uppercase tracking-wider mr-4">
                  Available Products
                </span>
              </div>
            </a>
            <div className="order-2 min-w-full sm:min-w-0 m-3 p-3 bg-white min-h-0 rounded shadow-md border-l-8 border-blue-600">
              <div className="text-5xl">211</div>
              <span className="font-bold text-gray-600 text-md text-secondary uppercase tracking-wider mr-4">
                Available Watersheds
              </span>
            </div>
            <div className="order-3 min-w-full sm:min-w-0 m-3 p-3 bg-white min-h-0 rounded shadow-md border-l-8 border-orange-600">
              <div className="text-5xl">350</div>
              <span className="font-bold text-gray-600 text-md text-secondary uppercase tracking-wider mr-4">
                Downloads this week
              </span>
            </div>
          </div>
          {/* <!--second row --> */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="m-3 p-3 bg-white min-h-0 shadow-md border-l-4 border-gray-600 rounded">
              <MyWatersheds />
            </div>
            <div className="m-3 p-3 bg-white min-h-0 shadow-md rounded">
              <Downloads />
            </div>
          </div>
        </div>
      </main>
    </>
  );
}

export default dashboard;
