const exploreMapBundle = {
  name: "exploreMap",

  getReducer: () => {
    const initialData = {
      layer: null,
      _mapKey: "exploreMap",
      _shouldInitialize: true,
      _shouldAddData: false,
      _mapLoaded: false,
      _instrumentsLoaded: false,
      _groupsLoaded: false,
    };

    return (state = initialData, { type, payload }) => {
      if (process.env.NODE_ENV === "development") console.log(type, payload);
      switch (type) {
        case "MAPS_INITIALIZED":
          if (payload.hasOwnProperty(initialData._mapKey)) {
            return Object.assign({}, state, {
              _mapLoaded: true,
            });
          } else {
            return state;
          }
        case "MAPS_SHUTDOWN":
          if (payload.hasOwnProperty(initialData._mapKey)) {
            return Object.assign({}, state, {
              _mapLoaded: false,
            });
          } else {
            return state;
          }
        case "EXPLOREMAP_INITIALIZE_START":
        case "EXPLOREMAP_INITIALIZE_FINISH":
          return Object.assign({}, state, payload);
        default:
          return state;
      }
    };
  },

  doExploreMapInitialize: () => ({ dispatch, store }) => {
    dispatch({
      type: "EXPLOREMAP_INITIALIZE_START",
      payload: {
        _shouldInitialize: false,
      },
    });

    dispatch({
      type: "EXPLOREMAP_INITIALIZE_FINISH",
      payload: {},
    });
  },

  selectExploreMapKey: (state) => {
    return state.exploreMap._mapKey;
  },

  reactExploreMapShouldInitialize: (state) => {
    if (state.exploreMap._shouldInitialize)
      return { actionCreator: "doExploreMapInitialize" };
  },
};

export default exploreMapBundle;
