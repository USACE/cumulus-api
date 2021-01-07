const appDefaultsBundle = {
  name: "appDefaults",

  getReducer() {
    const initialData = {
      formSelectPlaceholder: "Start typing to filter...",
    };

    return (state = initialData, { type, payload }) => {
      switch (type) {
        default:
          return state;
      }
    };
  },

  selectAppDefaultsRaw: (state) => {
    return state.appDefaults;
  },
  selectAppDefaultsFormSelectPlaceholder: (state) => {
    return state.appDefaults.formSelectPlaceholder;
  },
};

export default appDefaultsBundle;
