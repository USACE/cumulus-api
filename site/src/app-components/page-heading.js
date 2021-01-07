import React from "react";

export default function page_heading(props) {
  return (
    <>
      <div className="mb-3 pl-3">
        <h2 className="text-4xl font-medium font-bold text-gray-800 m-0">
          {props.heading}
        </h2>
        <div className="text-secondary text-gray-600 font-bold tracking-tight">
          {props.subHeading}
        </div>
      </div>
    </>
  );
}
