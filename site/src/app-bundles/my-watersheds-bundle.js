import { createSelector } from "redux-bundler";
import createRestBundle from "./create-rest-bundle";

const myWatershedsBundle = createRestBundle({
  name: "myWatersheds",
  uid: "slug",
  prefetch: true,
  staleAfter: 0,
  persist: false,
  routeParam: "ws_slug",
  getTemplate: "/my_watersheds",
  putTemplate: ":/",
  postTemplate: ":/",
  deleteTemplate: ":/",
  fetchActions: ["URL_UPDATED", "AUTH_LOGGED_IN"],
  forceFetchActions: [],
  urlParamSelectors: [],
  addons: {
    doMyWatershedsAdd: (watershed) => ({ store, dispatch }) => {
      dispatch({ type: "MYWATERSHEDS_ADD_START" });

      const apiRoot = store.selectApiRoot();
      const authToken = store.selectAuthTokenRaw();

      fetch(`${apiRoot}/my_watersheds/${watershed.id}/add`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + authToken,
        },
        body: JSON.stringify({}),
      })
        .then((response) => {
          if (!response.ok) {
            // Fire Nofitication
            store.doNotificationFire({
              level: "error",
              title: "My Watershed Add Failed",
              message: `Failed to Add Watershed: ${watershed.name}\nStatus Code: ${response.status}`,
            });
          }
          response.json();
        })
        .then((j) => {
          // Notification
          store.doNotificationFire({
            level: "success",
            title: "My Watershed Add",
            message: `Added Watershed: ${watershed.name}`,
          });
          // Fetch
          dispatch({
            type: "MYWATERSHEDS_ADD_FINISH",
            payload: { _shouldFetch: true },
          });
        });
    },
    doMyWatershedsRemove: (watershed) => ({ store, dispatch }) => {
      dispatch({ type: "MYWATERSHEDS_REMOVE_START" });

      const apiRoot = store.selectApiRoot();
      const authToken = store.selectAuthTokenRaw();

      const state = store.selectMyWatershedsState();
      const stateNew = { ...state };
      delete stateNew[watershed.slug];

      // Pre-Remove item from state for fast render
      dispatch({ type: "MYWATERSHEDS_UPDATED_ITEM", payload: stateNew });

      fetch(`${apiRoot}/my_watersheds/${watershed.id}/remove`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + authToken,
        },
        body: JSON.stringify({}),
      })
        .then((response) => {
          if (!response.ok) {
            // If API Request Fails...
            // Fire Nofitication
            store.doNotificationFire({
              level: "error",
              title: "My Watershed Remove Failed",
              message: `Failed to Removed Watershed: ${watershed.name}\nStatus Code: ${response.status}`,
            });
            // Restore Item We Pre-Removed from State
            dispatch({ type: "MYWATERSHEDS_UPDATED_ITEM", payload: state });
          }
          response.json();
        })
        .then((j) => {
          // Notification
          store.doNotificationFire({
            level: "success",
            title: "My Watershed Remove",
            message: `Removed Watershed: ${watershed.name}`,
          });
          // Finish
          dispatch({
            type: "MYWATERSHEDS_REMOVE_FINISH",
          });
        });
    },
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

  reduceFurther: (state, { type, payload }) => {
    switch (type) {
      case "MYWATERSHEDS_ADD_START":
      case "MYWATERSHEDS_ADD_FINISH":
      case "MYWATERSHEDS_REMOVE_START":
      case "MYWATERSHEDS_REMOVE_FINISH":
        return Object.assign({}, state, payload);
      default:
        return state;
    }
  },
});

export default myWatershedsBundle;
