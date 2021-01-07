import React, { useState } from "react";
import { connect } from "redux-bundler-react";
import moment from "moment";

function getProductAlias(p) {
  const aliases = {
    PRECIPITATION: "Precip",
    TEMPERATURE: "AirTemp",
    SNOW: "Snow",
  };
  if (Object.keys(aliases).includes(p)) {
    return aliases[p];
  }
  return p;
}

const Tabs = ({ tabs, setActiveTab, activeTab }) =>
  tabs && tabs.length
    ? tabs.map((t, idx) => (
        <button
          key={idx}
          onClick={(e) => {
            setActiveTab(t);
          }}
          className={`cursor-pointer py-4 px-6 block mr-1 
            focus:outline-none font-semibold rounded-t border-b-2 ${
              activeTab === t
                ? "border-blue-800 bg-gray-700 text-white"
                : "text-gray-600 hover:text-blue-600 hover:border-blue-800"
            }`}
        >
          {getProductAlias(t)}
        </button>
      ))
    : null;

export default connect(
  "selectProductByParameter",
  "selectProductParameters",
  ({ productByParameter: products, productParameters: tabs }) => {
    const [activeTab, setActiveTab] = useState(
      tabs && tabs.length ? tabs[0] : null
    );

    return (
      <>
        <div>{JSON.stringify(activeTab)}</div>
        <span className="font-bold text-gray-600 text-md text-secondary uppercase tracking-wider mr-4">
          Available Products
        </span>
        <div className="mt-3">
          {/* <nav classNme="bg-gray-200 mt-3"> */}
          <nav className="flex  sm:flex-row border-b-2 border-gray-400 bg-gray-200">
            <Tabs
              tabs={tabs}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
            />
          </nav>
        </div>

        {products &&
          !!activeTab &&
          products[activeTab].map((p, idx) => (
            <div key={idx}>
              <div className="overflow-ellipsis	overflow-hidden">
                <ul>
                  <li className="p-2 border-b-2">
                    {p.name}{" "}
                    <span className="block text-sm text-gray-600">
                      ({moment.utc(p.after).format("DD-MMM-YY")} -{" "}
                      {moment.utc(p.before).format("DD-MMM-YY")})
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          ))}
      </>
    );
  }
);
