import React, { useRef } from "react";
import classnames from "classnames";
import { connect } from "redux-bundler-react";

export default connect("doShapefileQueueZip", ({ doShapefileQueueZip }) => {
  const inputEl = useRef(null);

  const handleClick = (e) => {
    inputEl.current.click();
  };

  const handleInputChange = (e) => {
    inputEl.current.files.length &&
      doShapefileQueueZip(inputEl.current.files[0]);
  };

  const btnClass = classnames({
    "bg-transparent text-gray-200 font-semibold hover:text-white py-2 px-4 border border-gray-200 hover:border-transparent hover:bg-green-400 rounded-full block": true,
  });

  return (
    <>
      <button className={btnClass} onClick={handleClick}>
        Upload File
      </button>
      <input
        style={{ display: "none" }}
        ref={inputEl}
        type="file"
        onChange={handleInputChange}
      ></input>
    </>
  );
});
