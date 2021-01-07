import { createSelector } from "redux-bundler";
import createRestBundle from "./create-rest-bundle";

const watershedBundle = createRestBundle({
  name: "watershed",
  uid: "slug",
  prefetch: true,
  staleAfter: 10000,
  persist: false,
  routeParam: "ws_slug",
  getTemplate: "/watersheds",
  putTemplate: "/watersheds/:item.id",
  postTemplate: "/watersheds",
  deleteTemplate: "/watersheds/:item.id",
  fetchActions: ["URL_UPDATED", "AUTH_LOGGED_IN"],
  forceFetchActions: [],
  urlParamSelectors: [],
  sortBy: "office_symbol",
  sortAsc: true,
  addons: {
    selectWatershedFakeByRoute: createSelector(
      "selectWatershedByRoute",
      (watershed) => {
        if (!watershed || !Object.keys(watershed).length) {
          return {
            id: "d4c3c6ed-4745-4683-8287-563bba8f6ca4",
            name: "Apalachicola Chattahoochee Flint Rivers",
            x_min: 970000,
            y_min: 790000,
            x_max: 1162000,
            y_max: 1386000,
            office_symbol: "SAM",
          };
        }
        return watershed;
      }
    ),
  },
});

export default watershedBundle;
