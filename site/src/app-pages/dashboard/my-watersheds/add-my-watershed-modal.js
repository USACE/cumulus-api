import React, { useState } from "react";
import { connect } from "redux-bundler-react";

import Select from "react-select";

const AddMyWatershedModal = connect(
  "selectWatershedItemsArray",
  "doModalClose",
  ({ watershedItemsArray: watersheds, doModalClose, watershedSelected }) => {
    const [payload, setPayload] = useState({
      watershed_id: watershedSelected || null,
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      if (!payload || !payload.watershed_id) {
        console.log("Missing one or more required fields");
        return;
      }
      //   doDownloadRequest(payload);
      doModalClose();
    };
    return (
      <div
        className="inline-block overflow-visible align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-headline"
      >
        <form className="p-6" onSubmit={handleSubmit}>
          <fieldset>
            <legend className="mb-3 text-2xl">Select Watersheds</legend>

            <div className="mt-3">
              <label className="block mt-6 mb-2" forhtml="watershed">
                <span className="text-gray-700">Watershed</span>
              </label>
              <Select
                options={watersheds.map((w, index) => ({
                  value: w.id,
                  label: `${w.office_symbol} - ${w.name}`,
                }))}
                onChange={(selectedOption) => {
                  setPayload({
                    ...payload,
                    watershed_id: selectedOption.value,
                  });
                }}
              />
            </div>

            <div className="flex">
              <button
                onClick={handleSubmit}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 mt-10 rounded mt-3"
              >
                Submit
              </button>
              <button
                onClick={(e) => {
                  doModalClose();
                }}
                className="ml-3 bg-red-300 hover:bg-red-500 text-white font-bold py-2 px-4 mt-10 rounded mt-3"
              >
                Cancel
              </button>
            </div>
          </fieldset>
        </form>
      </div>
    );
  }
);

export default AddMyWatershedModal;
