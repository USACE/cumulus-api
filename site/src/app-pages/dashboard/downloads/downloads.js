import React from "react";
import { connect } from "redux-bundler-react";
import { DateTime } from "luxon";

import NewDownloadButton from "./new-download-button";

const HEADERS = ["Basin", "Requested", "Processing Time", "Download"];

const ProgressBar = ({ percent }) => {
  return (
    <div className="flex flex-col">
      {/* Percent Complete */}
      <div className="w-100 text-right">
        <span className="text-xs font-mono">{percent}%</span>
      </div>
      {/* Progress Bar */}
      <div
        className={`flex overflow-hidden h-2 mb-4 text-xs rounded bg-blue-200 ${
          percent < 100 && "animate-pulse"
        }`}
      >
        <div
          style={{ width: `${percent}%` }}
          className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
        ></div>
      </div>
    </div>
  );
};

const TableRow = ({ item }) => {
  const procStart = DateTime.fromISO(item.processing_start);
  const procEnd = DateTime.fromISO(item.processing_end);
  const dur = procEnd.diff(procStart, "seconds");

  const DownloadNow = ({ href }) => (
    <a href={href}>
      <svg
        className="w-6 text-gray-500 hover:text-gray-800"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        width="24"
      >
        <title>Click to Download</title>
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
        />
      </svg>
    </a>
  );

  const DownloadFailed = () => (
    <>
      <svg
        className="w-6 text-red-600"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 20"
        fill="currentColor"
        width="24"
      >
        <title>Failed Download</title>
        <path
          fillRule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
          clipRule="evenodd"
        />
      </svg>
    </>
  );

  return (
    <tr>
      {/* Basin */}
      <td className="p-2 text-left">{item.watershed_name}</td>
      {/* Requested */}
      <td className="p-2 text-left">{procStart.toRelativeCalendar()}</td>
      <td className="p-2 text-left">{`${parseInt(dur.as("seconds"))}s`}</td>
      <td className="">
        {item.status === "SUCCESS" && item.progress === 100 ? (
          <DownloadNow href={item.file} />
        ) : item.status === "INITIATED" ? (
          <ProgressBar percent={item.progress} />
        ) : item.status === "FAILED" ? (
          <DownloadFailed />
        ) : null}
      </td>
    </tr>
  );
};

const TableHeader = ({ title }) => (
  <th
    scope="col"
    className="px-1 py-3 bg-gray-100 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
  >
    {title}
  </th>
);

export default connect(
  "selectDownloadItemsArray",
  ({ downloadItemsArray: items }) => {
    return (
      <>
        <div className="flex justify-between">
          <div className="font-bold text-gray-600 text-md text-secondary uppercase tracking-wider mr-4">
            My Downloads
          </div>
          <div className="mr-2">
            <NewDownloadButton />
          </div>
        </div>

        <div className="h-96 block overflow-y-auto w-full">
          <table className="min-w-full divide-y divide-gray-200 mt-5">
            <thead>
              <tr>
                {HEADERS.map((h, idx) => (
                  <TableHeader title={h} />
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {items.map((item, index) => (
                <TableRow key={index} item={item} />
              ))}
            </tbody>
          </table>
        </div>
      </>
    );
  }
);
