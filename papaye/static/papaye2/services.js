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

.service('login', ['$http', function($http) {
	var username = "";

    return {
        getUsername: function() {
            return username;
        },

        setUsername: function(newUsername) {
            username = newUsername;
        },
    }
}])

.service('locationSaver', ['$location', function($location) {
    var locationUrl = null;

    return {
        storeLocation: function(NewLocationUrl) {
            locationUrl = NewLocationUrl;
        },

        recoverLocation: function() {
            $location.url(locationUrl);
        }
    }
}]); 
