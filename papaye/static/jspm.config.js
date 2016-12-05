SystemJS.config({
  paths: {
    "npm:": "jspm_packages/npm/",
    "github:": "jspm_packages/github/",
    "papaye/": "src/"
  },
  browserConfig: {
    "baseURL": "/static"
  },
  devConfig: {
    "map": {
      "plugin-babel": "npm:systemjs-plugin-babel@0.0.13"
    }
  },
  transpiler: "plugin-babel",
  packages: {
    "papaye": {
      "main": "js/main.js",
      "meta": {
        "*.js": {
          "loader": "plugin-babel"
        }
      }
    }
  }
});

SystemJS.config({
  packageConfigPaths: [
    "npm:@*/*.json",
    "npm:*.json",
    "github:*/*.json"
  ],
  map: {
    "backbone": "npm:backbone@1.3.3",
    "backbone.marionette": "npm:backbone.marionette@2.4.7",
    "backgrid": "github:wyuenho/backgrid@0.3.7",
    "bootstrap": "github:twbs/bootstrap@3.3.7",
    "css": "github:systemjs/plugin-css@0.1.27",
    "font-awesome": "npm:font-awesome@4.6.3",
    "fs": "github:jspm/nodelibs-fs@0.2.0-alpha",
    "handlebars": "github:components/handlebars.js@4.0.5",
    "highlightjs": "github:components/highlightjs@9.6.0",
    "inconsolata": "npm:inconsolata@0.0.2",
    "jquery": "npm:jquery@3.1.0",
    "noty": "npm:noty@2.3.8",
    "spinkit": "npm:spinkit@1.2.5",
    "text": "github:systemjs/plugin-text@0.0.8",
    "ubuntu-fontface": "npm:ubuntu-fontface@0.1.11",
    "underscore": "npm:underscore@1.8.3"
  },
  packages: {
    "npm:backbone.marionette@2.4.7": {
      "map": {
        "underscore": "npm:underscore@1.8.3",
        "backbone.babysitter": "npm:backbone.babysitter@0.1.12",
        "backbone": "npm:backbone@1.3.3",
        "backbone.wreqr": "npm:backbone.wreqr@1.3.7"
      }
    },
    "npm:backbone.babysitter@0.1.12": {
      "map": {
        "underscore": "npm:underscore@1.8.3",
        "backbone": "npm:backbone@1.3.3"
      }
    },
    "npm:backbone@1.3.3": {
      "map": {
        "underscore": "npm:underscore@1.8.3"
      }
    },
    "npm:backbone.wreqr@1.3.7": {
      "map": {
        "underscore": "npm:underscore@1.8.3",
        "backbone": "npm:backbone@1.3.3"
      }
    },
    "npm:font-awesome@4.6.3": {
      "map": {
        "css": "github:systemjs/plugin-css@0.1.26"
      }
    },
    "github:twbs/bootstrap@3.3.7": {
      "map": {
        "jquery": "npm:jquery@2.2.4"
      }
    },
    "github:wyuenho/backgrid@0.3.7": {
      "map": {
        "underscore": "npm:underscore@1.8.3",
        "backbone": "npm:backbone@1.2.3"
      }
    },
    "npm:backbone@1.2.3": {
      "map": {
        "underscore": "npm:underscore@1.8.3"
      }
    }
  }
});
