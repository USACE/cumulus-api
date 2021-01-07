import React from "react";
import Navbar from "../../app-components/navbar";
import PageHeading from "../../app-components/page-heading";
import { connect } from "redux-bundler-react";

import MyTokens from "./my-tokens";

export default connect(
  "selectProfileMyProfile",
  "selectAuthUsername",
  (props) => {
    const profile = props.profileMyProfile;
    const user = props.authUsername;

    function formatAuthUsername(username) {
      const parts = username.split(".");
      if (parts.length === 2) {
        return parts[0] + ", " + parts[1];
      } else {
        return parts[0] + ", " + parts[1] + " " + parts[2];
      }
    }

    return (
      <main className="bg-gray-200 h-full lg:h-screen">
        <Navbar />
        <div className="mx-auto max-w-screen-2xl sm:p-10">
          <PageHeading heading={formatAuthUsername(user)} subHeading={""} />

          {/* <!--first row --> */}
          <div className="grid grid-cols-1">
            <div className="m-3 p-3 bg-white min-h-0 shadow-md rounded">
              <div className="font-bold text-gray-600 text-md text-secondary uppercase tracking-wider inline">
                My Profile
              </div>
              <div className="grid grid-flow-col grid-cols-6 grid-rows-3 gap-4 p-4 border-gray-100 border-t-4">
                <div className="font-semibold text-lg">Name:</div>
                <div className="col-start-2 col-end-7 text-lg">
                  {formatAuthUsername(user)}
                </div>
                <div className="font-semibold text-lg">Email:</div>
                <div className="col-start-2 col-end-7 text-lg">
                  {profile.email}
                </div>
              </div>
            </div>
          </div>

          {/* <!--second row --> */}
          <div className="grid grid-cols-1">
            <div className="m-3 p-3 bg-white min-h-0 shadow-md rounded">
              <MyTokens />
            </div>
          </div>

          {/* <h2 className="mt-10 text-3xl text-gray-600">My Profile</h2>
          <div className="mb-10 grid grid-flow-col grid-cols-6 grid-rows-3 gap-4 border-gray-400 border-t-4 p-4">
            <div className="font-semibold text-lg">Name:</div>
            <div className="col-start-2 col-end-7 text-lg">
              {formatAuthUsername(user)}
            </div>
            <div className="font-semibold text-lg">Email:</div>
            <div className="col-start-2 col-end-7 text-lg">{profile.email}</div>
          </div>

          <MyTokens /> */}
        </div>
      </main>
    );
  }
);
