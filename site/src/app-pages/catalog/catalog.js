import React from "react";
import Navbar from "../../app-components/navbar";
import { connect } from "redux-bundler-react";
import moment from "moment";

const Availability = (p) => {
  const availability_fields = {
    From: "after",
    To: "before",
    "% Coverage": "percent_coverage",
    "Grid Count": "productfile_count",
  };

  const ListItem = ({ k }) => {
    return (
      <li>
        <div className="flex">
          <div className="font-bold w-32">{k}</div>
          {k === "From" || k === "To" ? (
            <p className="ml-4 font-mono">
              {moment
                .utc(p[availability_fields[k]])
                .format("DD MMM YYYY hh:mm z")}
              <span className="ml-4 italic text-xs">
                {moment.utc(p[availability_fields[k]]).fromNow()}
              </span>
            </p>
          ) : (
            <p className="ml-4 font-mono">{p[availability_fields[k]]}</p>
          )}
        </div>
      </li>
    );
  };
  return (
    <>
      <h1 className="text-lg">Availability</h1>
      <hr />
      <ul className="list-none mt-2">
        {Object.keys(availability_fields).map((k, idx) => {
          return <ListItem key={idx} k={k} />;
        })}
      </ul>
    </>
  );
};

const ProductSection = (p) => (
  <div className="shadow-lg hover:shadow-2xl">
    <a href={`/catalog/${p.id}`}>
      <div className="flex justify-between border border-blue-800 px-4 py-2 text-blue-800 rounded-t">
        <div className="text-lg font-bold ">{p.name}</div>
        <div className="font-light">
          {p.parameter}, {p.unit}
        </div>
      </div>

      <div className="flex border border-t-0 border-blue-800 rounded-b bg-gray-100 px-4 py-3 text-blue-700">
        {/* Image */}
        <div>
          <img
            className="rounded-lg md:w-56"
            src="https://images.unsplash.com/photo-1578924825042-31d14cf13c35?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=500&q=60"
            alt="Placeholder Map"
          />
        </div>
        {/* Availability */}
        <div className="ml-8 flex-grow">{Availability(p)}</div>

        {/* Metadata */}
        {/* {Metadata(p)} */}
      </div>
    </a>
  </div>
);

export default connect(
  "selectProductItemsArray",
  ({ productItemsArray: products }) => {
    return (
      <main>
        <Navbar />
        <div className="container mx-auto">
          <p className="mt-12 text-3xl">Available Products</p>
          <p>Ready for real-time modeling or historic calibration</p>
          <hr className="mt-4" />
          <div className="space-y-12 mt-10 mb-10 max-w-3xl">
            {products.map((p) => ProductSection(p))}
          </div>
        </div>
      </main>
    );
  }
);
