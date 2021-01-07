import React from "react";
import { connect } from "redux-bundler-react";
import TokenCreatedModal from "./token-created-modal";

const CreateTokenButton = connect(
  "selectAuthTokenRaw",
  "selectApiRoot",
  "doModalOpen",
  "doProfileFetch",
  ({ authTokenRaw: authToken, apiRoot, doModalOpen, doProfileFetch }) => {
    const handleClick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      fetch(`${apiRoot}/my_tokens`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + authToken,
        },
      })
        .then((response) => {
          if (!response.ok) {
            console.log("ERROR Creating Token");
            console.log(`Request returned a ${response.status}`);
          }
          return response.json();
        })
        .then((j) => {
          doModalOpen(TokenCreatedModal, { secretTokenInfo: j });
          doProfileFetch();
        });
    };

    return (
      <button
        onClick={handleClick}
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        Create Token <i className="mdi mdi-plus" />
      </button>
    );
  }
);

const DeleteTokenButton = connect(
  "doProfileTokenDelete",
  ({ doProfileTokenDelete, item }) => {
    const handleClick = (e) => {
      doProfileTokenDelete(item);
    };

    return (
      <button
        className="bg-red-400 py-2 px-4 text-white rounded hover:bg-red-600 hover:shadow-2xl"
        onClick={handleClick}
      >
        Delete
      </button>
    );
  }
);

export default connect("selectProfileTokens", ({ profileTokens: tokens }) => (
  <>
    <div className="flex flex-row justify-between mb-2">
      <span className="font-bold text-gray-600 text-md text-secondary uppercase tracking-wider inline">
        My Tokens
        <span className=" ml-3 px-2 py-1 rounded-full bg-blue-800 text-white rounded">
          {tokens.length}
        </span>
      </span>
      <CreateTokenButton />
    </div>
    <div className="border-gray-100 border-t-4">
      <div>
        {tokens.map((t, idx) => (
          <div
            key={idx}
            className="flex flex-row justify-between p-2 m-2 bg-gray-100"
          >
            <div className="flex flex-row">
              <DeleteTokenButton item={t} />
              <div className="ml-5 p-2 font-mono">{t.token_id}</div>
            </div>
            <div className="ml-2 p-2">{t.issued}</div>
          </div>
        ))}
      </div>
    </div>
  </>
));
