import React from "react";
import { connect } from "redux-bundler-react";

import AddMyWatershedModal from "./add-my-watershed-modal";

const AddMyWatershedButton = connect("doModalOpen", ({ doModalOpen }) => {
  return (
    <button
      onClick={(e) => {
        doModalOpen(AddMyWatershedModal, {});
      }}
    >
      + New
    </button>
  );
});

export default AddMyWatershedButton;
