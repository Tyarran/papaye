const path = require('path');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
    entry: './src/index.js', // string | object | array
    output: {
        filename: 'papaye.bundle.js',
        path: path.resolve('./dist')

    },
    mode: 'development',
    watch: true,

    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['react', 'es2015']
                    }
                }
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            },
            {
                test: /\.(ttf|eot|svg|otf|woff|woff2)$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            publicPath: 'dist/'
                        }
                    }
                ],
            }
        ]
    },

    plugins: [
        new UglifyJsPlugin() 
    ]
};
