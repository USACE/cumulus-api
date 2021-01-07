import React from "react";
import ReactDOM from "react-dom";
import { Provider } from "redux-bundler-react";
import { getNavHelper } from "internal-nav-helper";
import getStore from "./app-bundles";
import cache from "./cache";

import './index.css';
import App from "./App";

cache.getAll().then((initialData) => {
  const store = getStore(initialData);

  if (process.env.NODE_ENV === "development") window.store = store;

  ReactDOM.render(
    <Provider store={store}>
      <div onClick={getNavHelper(store.doUpdateUrlWithHomepage)}>
        <App />
      </div>
    </Provider>,
    document.getElementById("root")
  );
});
