import createRestBundle from "./create-rest-bundle";

export default createRestBundle({
  name: "productavailability",
  uid: "product_id",
  prefetch: true,
  staleAfter: 10000,
  persist: false,
  routeParam: "product_id",
  getTemplate: "/products/:product_id/availability",
  fetchActions: ["URL_UPDATED"],
  urlParamSelectors: ["selectProductIdByRoute"],
  forceFetchActions: [],
  sortBy: "name",
  sortAsc: true,
  addons: {},
});
