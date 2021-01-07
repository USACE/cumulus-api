import React from "react";
import Navbar from "../../app-components/navbar";

export default function Contact(props) {
  return (
    <main>
      <Navbar />
      <div className="text-center mt-12">
        <h1 className="text-5xl">
          <span className="font-light"> Need Help?</span>
        </h1>
        <p className="text-gray-800 mt-2 font-thin text-2xl">
          For technical assistance or general questions, send an email to:
          <br />
          <a href="mailto:CWMS-GriddedData-Support@usace.army.mil">
            CWMS-GriddedData-Support@usace.army.mil
          </a>
        </p>
      </div>
    </main>
  );
}
