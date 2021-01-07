import React from "react";
import { connect } from "redux-bundler-react";
import Loader from "../../../app-components/loader";
import AddMyWatershedButton from "./add-my-watershed-button";

// function basins(props) {
// const dummyItems = [
//   {
//     id: "7c6dd902-fbc5-43e4-9bbf-351963f5723d",
//     name: "Muskingum River",
//     office_symbol: "LRH",
//   },
//   {
//     id: "ced6ec9e-43b5-496e-a2b7-894af92c9b63",
//     name: "Mississippi River Navigation",
//     office_symbol: "MVP",
//   },
//   {
//     id: "0f065e6a-3380-4ac3-b576-89fae7774b9f",
//     name: "Little Sandy River",
//     office_symbol: "LRH",
//   },
// ];
export default connect(
  "selectMyWatershedsItemsArray",
  "selectMyWatershedsIsLoading",
  "doMyWatershedsRemove",
  ({
    myWatershedsItemsArray: watersheds,
    myWatershedsIsLoading: isLoading,
    doMyWatershedsRemove,
  }) =>
    isLoading ? (
      <Loader />
    ) : (
      <>
        <div className="font-bold text-gray-600 text-md text-secondary uppercase tracking-wider inline">
          My Watersheds
        </div>
        <div className="float-right">
          {/* <svg
            className="w-6 float-left"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            width="20"
          >
            <path
              fillRule="evenodd"
              d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
              clipRule="evenodd"
            />
          </svg> */}
          <AddMyWatershedButton />
        </div>
        <div className="h-96 block overflow-y-hidden w-full">
          <table className="w-full divide-y divide-gray-200 mt-5 ">
            <thead>
              <tr>
                <th
                  scope="col"
                  className="px-1 py-3 bg-gray-100 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Name
                </th>
                <th
                  scope="col"
                  className="px-1 py-3 bg-gray-100 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Office
                </th>
                <th
                  scope="col"
                  className="px-1 py-3 bg-gray-100 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="w-full bg-white divide-y divide-gray-200">
              {watersheds.map((w, index) => (
                <tr key={index}>
                  <td className="p-2 text-left">
                    <a href={`/ws/${w.slug}`}>
                      <span>{w.name}</span>
                    </a>
                  </td>
                  <td className="p-2 text-left">
                    {w.office_symbol || "OFFICE"}
                  </td>
                  <td>
                    <svg
                      className="w-6 cursor-pointer text-gray-500 hover:text-gray-800"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      width="24"
                      onClick={(e) => {
                        doMyWatershedsRemove(w);
                      }}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                      />
                    </svg>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </>
    )
);
