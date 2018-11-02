var hypernova = require('hypernova/server');
const test = require('/home/romain/Projects/papaye/papaye/static/src/components/test.jsx');
const index = require('./dist/papaye.bundle.js')

console.log(test);

hypernova({
  devMode: true,

  getComponent(name) {
    if (name === 'index.js') {
        return index;
    }
    if (name === 'test.jsx') {
        return test;
    }
    return null;
  },

  port: 3030,
});
