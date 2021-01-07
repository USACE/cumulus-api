import React from "react";

const Pill = ({ bgClass, iconClass, label }) => {
  return (
    <div className={` rounded-2xl px-1 mr-1 ${bgClass || "bg-gray-400"}`}>
      <div className="flex items-center p-1">
        <i className={`p-0 mdi mdi-light ${iconClass}`} />
        <span className="ml-1 text-white lowercase text-xs">{label}</span>
      </div>
    </div>
  );
};

export default Pill;
