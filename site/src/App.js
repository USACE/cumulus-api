import React from "react";
import Modal from "./app-components/modal";
import Notifications from "./app-components/notifications";
import "./css/mdi/css/materialdesignicons.min.css";
// import "./css/wireframe.css";

import { connect } from "redux-bundler-react";

export default connect("selectRoute", ({ route: Route }) => {
  return (
    <div>
      <Route />
      <Modal />
      <Notifications />
    </div>
  );
});
