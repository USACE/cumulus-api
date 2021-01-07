import React from "react";
import Navbar from "../../app-components/navbar";
import { connect } from "redux-bundler-react";
import Basin from "./basin";

export default connect("selectBasins", ({ basins }) => {
  // console.log("\n\n\n\n\n\n\n\n\n\n--these are the props--");
  // console.log(basins);
  return (
    <main>
      <Navbar />
      <div className="container mx-auto">
        <p className="mt-12 text-3xl">Basins</p>
        <p>Ready for real-time modeling or historic calibration</p>
        <hr className="mt-4 mb-4" />
        <span className="mr-5">Filter by Office:</span>
        <div className="inline-block relative w-64">
          <select className="block appearance-none w-full bg-white border border-gray-400 hover:border-gray-500 px-4 py-2 pr-8 rounded shadow leading-tight focus:outline-none focus:shadow-outline">
            <option>Show All</option>
            <option>Option 1</option>
            <option>Option 2</option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
            <svg
              class="fill-current h-4 w-4"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
            >
              <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
            </svg>
          </div>
        </div>
        <div className="space-y-12 mt-10 mb-10 max-w-3xl">
          {/* {JSON.stringify(basins)} */}
          {basins &&
            basins.length &&
            basins.map((b, idx) => <Basin key={idx} item={b} />)}
        </div>
      </div>
    </main>
  );
});
