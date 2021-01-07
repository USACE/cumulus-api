import {
  appTimeBundle,
  createDebugBundle,
  asyncCountBundle,
  composeBundlesRaw,
  createCacheBundle,
  createReactorBundle,
  createUrlBundle,
} from "redux-bundler";

import {
  createOlMapBundle,
  createOlBasemapBundle,
} from "@corpsmap/corpsmap-bundles";
import createNestedUrlBundle from "./create-nested-url-bundle";
import createAuthBundle from "./create-auth-bundle";
import createJwtApiBundle from "./create-jwt-api-bundle";
import pkg from "../../package.json";

import routeBundle from "./routes-bundle";
import shapefileBundle from "./shapefile-bundle";
import mapsBundle from "./maps-bundle";
import notificationBundle from "./notification-bundle";
import selectBundle from "./select-bundle";

import cache from "./../cache.js";
import productBundle from "./product-bundle";
import productAvailabilityBundle from "./product-availability-bundle";
import exploreMapBundle from "./explore-map-bundle";
import profileBundle from "./profile-bundle";
import modalBundle from "./modal-bundle";
import watershedBundle from "./watershed-bundle";
import downloadBundle from "./download-bundle";
import myWatershedsBundle from "./my-watersheds-bundle";

const mockTokenTestUser =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwIiwibmFtZSI6IlVzZXIuVGVzdCIsImlhdCI6MTUxNjIzOTAyMiwiZXhwIjoyMDAwMDAwMDAwLCJyb2xlcyI6WyJQVUJMSUMuVVNFUiJdfQ.q7TG-5QKo19raWrTz2A7639tB-V7RKJMPJ5-4qwdNd4";

export default composeBundlesRaw(
  // start of out-of-the-box bundles typically included with composeBundles()
  // composeBundlesRaw() used to customize createReactorBundle();
  appTimeBundle,
  asyncCountBundle,
  createUrlBundle(),
  createReactorBundle({ idleTimeout: 5000 }),
  createDebugBundle(),
  // end of out-of-the-box bundles
  createAuthBundle({
    appId: "20a4794c-91c3-4080-a42c-d9c0bda332a4",
    redirectOnLogout: pkg.homepage,
    mock: process.env.NODE_ENV === "development" ? true : false,
    token: process.env.NODE_ENV === "development" ? mockTokenTestUser : null,
  }),
  createJwtApiBundle({
    root:
      process.env.NODE_ENV === "development"
        ? `http://localhost/cumulus/v1`
        : `https://cumulus-api.rsgis.dev/cumulus/v1`,
    unless: {
      // GET requests do not include token unless path starts with /my_
      // Need token to figure out who "me" is
      custom: ({ method, path }) => {
        if (method === "GET") {
          if (path.slice(0, 4) === "/my_") {
            return false;
          }
          return true;
        }
        return false;
      },
    },
  }),
  createCacheBundle({
    cacheFn: cache.set,
  }),
  createUrlBundle(),
  createNestedUrlBundle({
    pkg: pkg,
  }),
  createOlBasemapBundle(),
  createOlMapBundle({
    name: "map",
    center: [-80.79, 26.94],
    zoom: 5,
  }),
  selectBundle,
  downloadBundle,
  mapsBundle,
  exploreMapBundle,
  productBundle,
  productAvailabilityBundle,
  routeBundle,
  shapefileBundle,
  notificationBundle,
  profileBundle,
  modalBundle,
  watershedBundle,
  myWatershedsBundle
);
