import { createSelector } from "redux-bundler";

const profileBundle = {
  name: "profile",
  getReducer: () => {
    const initialState = {
      _shouldFetch: false,
      myProfile: {},
    };

    return (state = initialState, { type, payload }) => {
      switch (type) {
        case "PROFILE_FETCH_START":
          return Object.assign({}, state, { _shouldFetch: false });
        case "PROFILE_FETCH_FINISH":
          return Object.assign({}, state, { myProfile: payload });
        case "PROFILE_TOKEN_DELETE_FINISH":
        case "AUTH_LOGGED_IN":
        case "AUTH_VERIFY_TOKEN":
        case "PROFILE_SAVED":
          return Object.assign({}, state, { _shouldFetch: true });
        case "PROFILE_TOKEN_DELETE_START":
          return state;
        default:
          return state;
      }
    };
  },
  doProfileFetch: () => ({ store, dispatch }) => {
    dispatch({ type: "PROFILE_FETCH_START" });

    const apiRoot = store.selectApiRoot();
    const token = store.selectAuthTokenRaw();

    fetch(`${apiRoot}/my_profile`, {
      headers: { Authorization: "Bearer " + token },
    })
      .then((resp) => {
        console.log(resp.status);
        if (resp.status === 404) {
          console.log("New User; Redirect to /profile/create");
          store.doUpdateUrlWithHomepage("/profile/create");
          return {};
        }
        return resp.json();
      })
      .then((j) => {
        console.log(j);
        dispatch({ type: "PROFILE_FETCH_FINISH", payload: j });
      })
      .catch((err) => {
        console.log(err);
      });
  },
  doProfileSave: (payload) => ({ store, dispatch }) => {
    const apiRoot = store.selectApiRoot();
    const authToken = store.selectAuthTokenRaw();

    fetch(`${apiRoot}/profiles`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + authToken,
      },
      body: JSON.stringify(payload),
    })
      .then((response) => {
        if (!response.ok) {
          console.log("ERROR!!!!!!!!!!!");
          console.log(`Request returned a ${response.status}`);
        }
        response.json();
      })
      .then((j) => {
        dispatch({ type: "PROFILE_SAVED" });
        store.doUpdateUrlWithHomepage("/profile");
      });
  },
  doProfileTokenDelete: (item) => ({ store, dispatch }) => {
    dispatch({ type: "PROFILE_TOKEN_DELETE_START" });

    const apiRoot = store.selectApiRoot();
    const authToken = store.selectAuthTokenRaw();

    fetch(`${apiRoot}/my_tokens/${item.token_id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + authToken,
      },
    })
      .then((response) => {
        if (!response.ok) {
          console.log("Error!");
          console.log(`Request returned a ${response.status}`);
        }
        response.json();
      })
      .then((j) => {
        dispatch({ type: "PROFILE_TOKEN_DELETE_FINISH" });
      });
  },
  selectProfileRaw: (state) => state.profile,
  selectProfileShouldFetch: (state) => state.profile._shouldFetch,
  selectProfileMyProfile: (state) => state.profile.myProfile,
  selectProfileTokens: createSelector("selectProfileMyProfile", (profile) =>
    profile && profile.tokens && profile.tokens.length ? profile.tokens : []
  ),
  reactProfileShouldFetch: createSelector(
    "selectProfileShouldFetch",
    (shouldFetch) => {
      if (!shouldFetch) {
        return null;
      }
      return { actionCreator: "doProfileFetch" };
    }
  ),
};

export default profileBundle;
