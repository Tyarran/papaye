'use strict';

papaye.controller('MainController', ['$scope', function($scope){
    $scope.main = {
        'title': 'Home'
    };

}])

.controller('ListPackageController', ['$scope', '$location', 'Package', function($scope, $location, Package) {
    $scope.packages = Package.query();

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
}]);
