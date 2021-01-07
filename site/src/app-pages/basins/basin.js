import React from "react";
// import { connect } from "redux-bundler-react";

export default function Basin({ item }) {
  return (
    <>
      {/* {JSON.stringify(item)} */}
      {/* {console.log(basins["basinsMyBasins"])} */}

      <div className="max-w-sm w-full lg:max-w-full lg:flex">
        <div
          className="bg-gray-300 h-48 lg:h-auto lg:w-48 flex-none bg-cover rounded-t lg:rounded-t-none lg:rounded-l text-center overflow-hidden"
          // style={{
          //   backgroundImage:
          //     "url(" +
          //     "https://images.unsplash.com/photo-1580715911453-d6d9cffd5771?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1337&q=80" +
          //     ")",
          //   backgroundPosition: "center bottom",
          //   //backgroundColor: "rgba(0, 0, 0, 0.5)",
          //   opacity: 0.2,
          // }}
          title="watershed extents"
        >
          <p className="text-5xl pt-8 text-gray-500">{item.office_symbol}</p>
        </div>
        <div className="border-r border-b border-l border-gray-400 lg:border-l-0 lg:border-t lg:border-gray-400 bg-white rounded-b lg:rounded-b-none lg:rounded-r p-4 flex flex-col justify-between leading-normal">
          <div className="mb-8">
            <div className="text-gray-900 font-bold text-xl mb-2">
              {item.name}
            </div>
            <p className="text-gray-700 text-base">
              Lorem ipsum dolor sit amet, consectetur adipisicing elit.
            </p>
          </div>
          {/* <div className="flex items-center">
          <img
            className="w-10 h-10 rounded-full mr-4"
            src="/img/jonathan.jpg"
            alt="Avatar of Jonathan Reinink"
          />
          <div className="text-sm">
            <p className="text-gray-900 leading-none">Jonathan Reinink</p>
            <p className="text-gray-600">Aug 18</p>
          </div>
        </div> */}
        </div>
      </div>
    </>
  );
}
