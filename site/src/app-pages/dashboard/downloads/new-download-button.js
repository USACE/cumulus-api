import React from "react";
import { connect } from "redux-bundler-react";

import NewDownloadModal from "./new-download-modal";

const NewDownloadButton = connect("doModalOpen", ({ doModalOpen }) => {
  return (
    <button
      onClick={(e) => {
        doModalOpen(NewDownloadModal, {});
      }}
    >
      + New
    </button>
  );
});

export default NewDownloadButton;
