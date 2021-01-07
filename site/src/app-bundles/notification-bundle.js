const notificationBundle = {
  name: "notification",

  getReducer() {
    const initialData = {
      options: null,
    };

    return (state = initialData, { type, payload }) => {
      switch (type) {
        case "NOTIFICATION_FIRE":
          return Object.assign({}, state, payload);
        case "NOTIFICATION_CLEAR":
          return Object.assign({}, state, { options: null });
        default:
          return state;
      }
    };
  },

  doNotificationFire: (options) => ({ dispatch }) => {
    dispatch({ type: "NOTIFICATION_FIRE", payload: { options } });
  },

  doNotificationClear: () => ({ dispatch }) => {
    dispatch({ type: "NOTIFICATION_CLEAR" });
  },

  selectNotification: (state) => {
    return state.notification.options;
  },
};

export default notificationBundle;
