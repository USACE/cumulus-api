import React from "react";
import Navbar from "../../app-components/navbar";
import { CardDocs, CardExplore, CardCatalog } from "../../app-components/cards";
// import background from "../../img/clouds.jpg";

const Home = () => (
  <main>
    {/* <div
      className="bg-auto"
      style={{
        backgroundImage: "url(" + background + ")",
        backgroundRepeat: "no-repeat",
        backgroundSize: "cover",
        backgroundPosition: "center",
        position: "absolute",
        width: "100%",
        height: "400px",
        opacity: "0.8",
        zIndex: "0",
      }}
    ></div> */}
    <Navbar />
    <div className="container mx-auto px-20">
      <div className="mt-12 p-4 rounded flex mx-auto bg-red-200">
        This application is under active development. We're deploying new
        progress early and often. Please expect to find buttons that do not go
        anywhere and incomplete features until this banner is taken down.
      </div>
      <div className="text-center mt-12">
        <h1 className="text-5xl">
          <strong className="font-sans font-black">Meteorology</strong>
          <span className="font-light"> With Simple Data Access</span>
        </h1>
        <p className="text-gray-800 mt-2 font-thin text-2xl">
          Realtime Processing Engine and REST API to Support Hydrologic Modeling
        </p>
      </div>

      <div className="container mt-24 mx-auto flex justify-around">
        <CardExplore />
        <CardCatalog />
        <CardDocs />
      </div>

      <div className="container mx-auto mt-12 text-center text-2xl">
        Need Help? <a href="/contact">Contact the support team.</a>
      </div>

      <div className="container mx-auto mt-12">
        <p className="font-light text-center italic">
          Connecting Modelers with Meteorological Data
        </p>
      </div>
    </div>
  </main>
);

export default Home;
