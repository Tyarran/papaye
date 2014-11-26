'use strict';

papaye.factory('Package', ['$resource',
    function($resource){
        return $resource(
            '/api/package/:packageName/:version/json',
            {packageName:'@name', version:'@version'},
            {'all': {method: 'GET', isArray: false}}
        );
    }]
)

.service('login', ['$http', '$location', function($http, $location) {
	var username = "";

    return {
        getUsername: function() {
            return username;
        },

        setUsername: function(newUsername) {
            username = newUsername;
        },

        logout: function($scope) {
            $http({
                url: '/logout',
                method: 'get',
            }).
            success(function(data, status, headers, config) {
                $location.url('/login');
            }).
            error(function(data, status, headers, config) {
                alert('NOK');
            });
        },
    }
}]);
