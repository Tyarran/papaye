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
	var username = "",
        scope = null;

    return {
        getUsername: function() {
            return username;
        },

        setUsername: function(newUsername) {
            username = newUsername;
            scope.refresh();
        },


        setScope: function(newScope) {
            scope = newScope;
        },

        logout: function($scope) {
            var setUsername = this.setUsername;

            $http({
                url: '/logout',
                method: 'get',
            }).
            success(function(data, status, headers, config) {
                setUsername('');
                noty({text: 'You are now disconnected', type: "success", layout: "bottom", timeout: 5000});
                $location.url('/login');
            }).
            error(function(data, status, headers, config) {
                alert('NOK');
            });
        },
    }
}]);
