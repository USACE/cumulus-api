// import { createSelector } from "redux-bundler";

// const basinBundle = {
//   name: "basins",
//   getReducer: () => {
//     const initialState = {
//       _shouldFetch: true,
//       data: [],
//     };

//     return (state = initialState, { type, payload }) => {
//       switch (type) {
//         case "BASINS_FETCH_START":
//         case "BASINS_FETCH_FINISH":
//           return Object.assign({}, state, payload);
//         // case "PROFILE_TOKEN_DELETE_FINISH":
//         // case "AUTH_LOGGED_IN":
//         // case "AUTH_VERIFY_TOKEN":
//         // case "PROFILE_SAVED":
//         //   return Object.assign({}, state, { _shouldFetch: true });
//         // case "PROFILE_TOKEN_DELETE_START":
//         //   return state;
//         default:
//           return state;
//       }
//     };
//   },
//   doBasinsFetch: () => ({ store, dispatch }) => {
//     dispatch({ type: "BASINS_FETCH_START", payload: { _shouldFetch: false } });

//     const apiRoot = store.selectApiRoot();
//     // const token = store.selectAuthTokenRaw();

//     fetch(`${apiRoot}/basins`, {
//       //   headers: { Authorization: "Bearer " + token },
//     })
//       .then((resp) => {
//         console.log(resp.status);
//         if (resp.status === 404) {
//           console.log("404 Error");
//           //   store.doUpdateUrlWithHomepage("/profile/create");
//           return {};
//         }
//         console.log("FETCHING BASINS FROM API");
//         console.log(`${apiRoot}/basins`);
//         return resp.json();
//       })
//       .then((j) => {
//         console.log(j);
//         dispatch({ type: "BASINS_FETCH_FINISH", payload: { data: j } });
//       })
//       .catch((err) => {
//         console.log(err);
//       });
//   },
//   //   selectProfileRaw: (state) => state.profile,
//   selectBasinsShouldFetch: (state) => state.basins._shouldFetch,
//   selectBasins: (state) => state.basins.data,
//   reactBasinsShouldFetch: createSelector(
//     "selectBasinsShouldFetch",
//     (shouldFetch) => {
//       if (!shouldFetch) {
//         return null;
//       }
//       return { actionCreator: "doBasinsFetch" };
//     }
//   ),
// };

// export default basinBundle;
