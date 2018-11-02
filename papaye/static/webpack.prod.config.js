const path = require('path');
const MinifyPlugin = require('babel-minify-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: './src/app.js', // string | object | array
    output: {
        //filename: 'papaye.bundle2.js',
        filename: '[name].js',
        path: path.resolve('./dist')

    },
    target: "node",
    // devtool: 'source-map',
    mode: 'production',
    //watch: true,

    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: 'babel-loader',
                }
            },
            {
                test: /\.css$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader'
                ]
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
        new MinifyPlugin(),
        new MiniCssExtractPlugin({
            filename: '[name].css',
            chunkFilename: '[id].css'
        })
    ]
};
