import React from "react";

import cfg from "../../package.json";

// https://tailwindcomponents.com/component/error-404
export default function FourOhFour() {
  const url = `${cfg.homepage}`;
  return (
    <>
      <div className="h-screen w-screen bg-green-400 flex justify-center content-center flex-wrap">
        <p style={{ fontSize: "220px" }} className="font-sans text-white">
          404
        </p>
      </div>

      <div className="absolute w-screen bottom-0 mb-6 text-white text-center font-sans text-xl">
        <span className="opacity-50">Take me back to </span>
        <a className="border-b" href={url}>
          {url}
        </a>
      </div>
    </>
  );
}
