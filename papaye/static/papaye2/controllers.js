'use strict';

var BaseChildController = function($scope, title, pageName) {
    //console.log('this:', this);
    
    $scope.$parent.login = {
        username: $scope.loginService.getUsername(),
    };

    $scope.$parent.main = {
        title: title,
    }

    if (pageName !== undefined) {
        $scope.$parent.activePage = pageName;
    }
};

papaye.controller('MainController', ['$scope', '$route', '$http', '$location', 'login', function($scope, $route, $http, $location, login){
    $scope.loginService = login

    $scope.login = {
        username: login.getUsername(),
    };

    $scope.pages = [['Home', '#/'], ['Browse', '#/browse']];

    $scope.logout = function() {
        $http({
            url: '/logout',
            method: 'get',
        }).
        success(function(data, status, headers, config) {
            login.setUsername('');
            noty({text: 'You are now disconnected', type: "success", layout: "bottom", timeout: 5000});
            $location.path('/reload/');
        }).
        error(function(data, status, headers, config) {
            alert('NOK');
        });
    };
    
    $scope.activePage = "Home";
}])

.controller('HomeController', ['$scope', '$location', '$route', '$injector', 'Package', function($scope, $location, $route, $injector, Package) {
    $injector.invoke(BaseChildController, this, {$scope: $scope, title: 'Home', pageName: 'Home'});
    var port = ($location.port() !== 80) ? ':' + $location.port(): '';

    $scope.simpleUrl = $location.protocol() + '://' + $location.host() + port + '/simple/';
}])

.controller('ListPackageController', ['$scope', '$location', '$route', '$injector', '$filter', 'Package', function($scope, $location, $route, $injector, $filter, Package) {
    $injector.invoke(BaseChildController, this, {$scope: $scope, title: 'Package list', pageName: 'Browse'});
    Package.all(function(response) {
        $scope.packages = response.result;
    });

    $scope.search = null;

    $scope.emptySearch = function() {
        $scope.search = null;
    }

    $scope.filterPackageList = function() {
        return $filter('filter')($scope.packages, $scope.search);
    }

    $scope.selectPackage = function(packageId) {
        $location.url('/browse/#'.replace('#', packageId));
    }

}])

.controller('SinglePackageController', ['$scope', '$sce', '$routeParams', '$injector', 'Package', function($scope, $sce, $routeParams, $injector, Package) {
    var name = $routeParams.name,
        version = null;

    $injector.invoke(BaseChildController, this, {$scope: $scope, title: 'Package ' + name, pageName: 'Browse'});
    if ($routeParams.version !== undefined) {
        version = $routeParams.version;
    }
    $scope.activeTab = 'current';
    $scope.error = null;
    $scope.release = Package.get({packageName: name, version: version}, function(release) {
        if (release.metadata) {
            $scope.description = $sce.trustAsHtml(release.metadata.description.content);
            $scope.htmlDescription = release.metadata.description.html;
        }
        $scope.error = 200;
    }, function(error) {
        $scope.error = 404;
    });

    $scope.tabClick = function(index) {
        if (index == 1) {
            $scope.activeTab = 'current';
        }
        else {
            $scope.activeTab = 'other';
        }
    };
}])

.controller('LoginController', ['$scope', '$http', '$location', '$injector', 'login', 'locationSaver', function($scope, $http, $location, $injector, login, locationSaver) {
    $injector.invoke(BaseChildController, this, {$scope: $scope, title: 'Login', pageName: undefined});
    $scope.sendForm = function(loginForm) {
        if (loginForm.$valid) {
            $http({
                url: '/login',
                method: 'POST',
                data: $.param({login: $scope.identifiant.username, password: $scope.identifiant.password}),
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            }).
            success(function(data, status, headers, config) {
                login.setUsername(data);
                noty({text: 'You are now connected', type: "success", layout: "bottom", timeout: 5000});
                console.log("logged");
                locationSaver.recoverLocation();
            }).
            error(function(data, status, headers, config) {
                noty({text: 'Identification failed', type: "error", layout: "bottom", timeout: 5000});
            });
        }
    }
}])

.controller('ReloaderController', ['locationSaver', function(locationSaver) {
    locationSaver.recoverLocation();
}]);
