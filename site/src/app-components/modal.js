import React from "react";
import { connect } from "redux-bundler-react";

// Markup for modal sourced from free
// Tailwind UI Preview Components
// https://tailwindui.com/preview

export default connect(
  "selectModalContent",
  "selectModalProps",
  "doModalClose",
  ({ modalContent: ModalContent, modalProps }) => {
    return !ModalContent ? null : (
      <div className="fixed z-10 inset-0 overflow-y-auto">
        <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          {/* <!--
      Background overlay, show/hide based on modal state.

      Entering: "ease-out duration-300"
        From: "opacity-0"
        To: "opacity-100"
      Leaving: "ease-in duration-200"
        From: "opacity-100"
        To: "opacity-0"
    --> */}
          <div className="fixed inset-0 transition-opacity">
            <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
          </div>
          {/* <!-- This element is to trick the browser into centering the modal contents. --> */}
          <span className="hidden sm:inline-block sm:align-middle sm:h-screen"></span>
          &#8203;
          {/* <!--
      Modal panel, show/hide based on modal state.

      Entering: "ease-out duration-300"
        From: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
        To: "opacity-100 translate-y-0 sm:scale-100"
      Leaving: "ease-in duration-200"
        From: "opacity-100 translate-y-0 sm:scale-100"
        To: "opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
    --> */}
          <ModalContent {...modalProps} />
        </div>
      </div>
    );
  }
);
