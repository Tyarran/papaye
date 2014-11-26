'use strict';

papaye.controller('MainController', ['$scope', 'login', function($scope, login){
    $scope.main = {
        'title': 'Home',
    };
    $scope.login = {
        username: login.getUsername(),
    };

    $scope.logout = function() {
        login.setUsername("");
        login.logout($scope);
        $scope.refresh();
    }

    $scope.refresh = function() {
        $scope.login.username = login.getUsername();
    }
}])

.controller('ListPackageController', ['$scope', '$location', 'Package', function($scope, $location, Package) {
    Package.all(function(response) {
        $scope.packages = response.result;
        $scope.packageCount = response.count;
    });

    $scope.selectPackage = function(packageId) {
        $location.path('/package/#'.replace('#', packageId));
    }

}])

.controller('SinglePackageController', ['$scope', '$sce', '$routeParams', 'Package', function($scope, $sce, $routeParams, Package) {
    var name = $routeParams.name,
        version = null;
    if ($routeParams.version !== undefined) {
        version = $routeParams.version;
    }
    $scope.activeTab = 'current';
    $scope.error = null;
    $scope.release = Package.get({packageName: name, version: version}, function(release) {
        $scope.description = $sce.trustAsHtml(release.metadata.description.content);
        $scope.htmlDescription = release.metadata.description.html;
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

.controller('LoginController', ['$scope', '$http', '$location', 'login', function($scope, $http, $location, login) {
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
                $scope.$parent.refresh();
                $location.url('/');
            }).
            error(function(data, status, headers, config) {
                noty({text: 'An error has occurred', type: "error", layout: "bottom", timeout: 5000});
                alert('NOK');
            });
        }
        else {
            alert("Pas valide");
        }
    }
}]);
