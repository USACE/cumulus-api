const modalBundle = {
  name: "modal",
  getReducer: () => {
    const initialData = {
      content: null,
      props: null,
    };

    return (state = initialData, { type, payload }) => {
      if (type === "MODAL_UPDATED") {
        return Object.assign({}, state, payload);
      }
      return state;
    };
  },
  doModalOpen: (content, props) => ({ dispatch }) => {
    dispatch({
      type: "MODAL_UPDATED",
      payload: {
        content: content,
        props: props,
      },
    });
  },
  doModalClose: () => ({ dispatch }) => {
    dispatch({
      type: "MODAL_UPDATED",
      payload: {
        content: null,
      },
    });
  },
  selectModalContent: (state) => state.modal.content,
  selectModalProps: (state) => state.modal.props,
};

export default modalBundle;
