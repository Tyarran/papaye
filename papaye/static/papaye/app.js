'use strict';

var papaye = angular.module('papaye', ['ngRoute', 'ngResource'])

.config(['$routeProvider', function($routeProvider) {
    var checkIsConnected = function($q, $timeout, $http, $location, login) {
        var deferred = $q.defer(),
            url = $location.$$url;
            console.log(url);
    
        $http.get('/islogged', {responseType: 'json'}).success(function(data, status, headers, config) {
            login.setUsername(data);
            $timeout(deferred.resolve, 0);
        })
        .error(function(data, status, headers, config) {
            if (status == 401) {
                login.setUsername("");
                if (url !== '/') {
                    $location.url('/login/' + url.slice(1).replace('/', '-'));
                }
                else {
                    $location.url('/login');
                }
            }
            else {
                noty({text: 'An error has occurred', type: "error", layout: "bottom", timeout: 5000});
            }
        });
        
        return deferred.promise;
    };
    $routeProvider.when('/', {
        templateUrl: 'static/papaye/partials/list_packages.html',
        controller: 'ListPackageController',
        resolve: {
            connected: checkIsConnected
        }
    })
    $routeProvider.when('/login', {
        templateUrl: 'static/papaye/partials/login.html',
        controller: 'LoginController',
    })
    $routeProvider.when('/login/:to', {
        templateUrl: 'static/papaye/partials/login.html',
        controller: 'LoginController',
    })
    .when('/package/:name', {
        templateUrl: 'static/papaye/partials/package.html',
        controller: 'SinglePackageController',
        resolve: {
            connected: checkIsConnected
        }
    })
    .when('/package/:name/:version', {
        templateUrl: 'static/papaye/partials/package.html',
        controller: 'SinglePackageController',
        resolve: {
            connected: checkIsConnected
        }
    })
    .otherwise({
        redirectTo: '/'
    });
}
]);
