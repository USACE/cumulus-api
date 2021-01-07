import React from "react";
import Navbar from "../../app-components/navbar";

export default function Admin({ children }) {
  return (
    <>
      <Navbar />
      <div className="flex mb-4">
        <div className="w-1/5 bg-blue-200"></div>
        <div className="w-4/5 bg-gray-100">
          <div className="mt-4 p-4 flex">
            <a
              className="border-b-2 border-gray-200 hover:border-green-400"
              href="/admin/shapeloader"
            >
              Shape Loader
            </a>
          </div>
          {children}
        </div>
      </div>
    </>
  );
}
