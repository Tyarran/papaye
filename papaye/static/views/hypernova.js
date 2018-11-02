'use strict';

var hypernova = require('hypernova/server');
var test = require('/home/romain/Projects/papaye/papaye/static/src/components/test.jsx');
var index = require('./dist/papaye.bundle.js');

console.log(test);

hypernova({
  devMode: true,

  getComponent: function getComponent(name) {
    if (name === 'index.js') {
      return index;
    }
    if (name === 'test.jsx') {
      return test;
    }
    return null;
  },


  port: 3030
});