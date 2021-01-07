import Url from "url-parse";
import { createSelector } from "redux-bundler";

export default function createNestedUrlBundle(options) {
  const defaults = {
    name: "nestedUrl",
    pkg: null,
    addons: {},
  };

  const config = Object.assign({}, defaults, options);

  return Object.assign(
    {},
    {
      name: config.name,

      getReducer: () => {
        const initialData = {
          pkg: config.pkg,
        };
        return (state = initialData, { type, payload }) => {
          return state;
        };
      },

      doUpdateUrlWithHomepage: (path) => ({ store }) => {
        const pkg = store.selectPackageInfo();
        if (!pkg || !pkg.homepage) return store.doUpdateUrl(path);
        store.doUpdateUrl(`${pkg.homepage}${path}`);
      },

      selectPackageInfo: (state) => {
        return state[config.name].pkg;
      },

      selectHomepage: createSelector("selectPackageInfo", (pkg) => {
        if (!pkg || !pkg.homepage) return "";
        const url = new Url(pkg.homepage);
        return url.pathname;
      }),

      selectPathnameMinusHomepage: createSelector(
        "selectPathname",
        "selectHomepage",
        (pathname, homepage) => {
          const matcher = new RegExp(homepage);
          return pathname.replace(matcher, "");
        }
      ),

      selectPublicFolder: createSelector("selectHomepage", (homepage) => {
        if (process.env.NODE_ENV !== "production") return "";
        return `${homepage}/`;
      }),
    },
    config.addons
  );
}
