'use strict';

var papaye = angular.module('papaye', ['ngRoute', 'ngResource'])


.config(['$routeProvider', function($routeProvider) {
    console.log('router');
    $routeProvider.when('/', {
        templateUrl: 'static/papaye/partials/list_packages.html',
        controller: 'ListPackageController',
    })
    .when('/package/:name', {
        templateUrl: 'static/papaye/partials/package.html',
        controller: 'SinglePackageController',
    })
    .when('/package/:name/:version', {
        templateUrl: 'static/papaye/partials/package.html',
        controller: 'SinglePackageController',
    })
    .otherwise({
        redirectTo: '/'
    });
}
])


.factory('Package', ['$resource',
    function($resource){
        return $resource('/api/package/:packageName/:version/json', {packageName:'@name', version:'@version'}); 
    }]
);
