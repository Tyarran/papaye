(function(H) {

    H.registerHelper('ifIsZero', function(value, options) {
        if(value === 0) {
            return options.fn(this);
        }
        return options.inverse(this);
    });
    
})(Handlebars);
