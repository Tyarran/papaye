const path = require('path');
//const MinifyPlugin = require('babel-minify-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const nodeExternals = require('webpack-node-externals');
const CleanWebpackPlugin = require('clean-webpack-plugin');


const clientConfig = {
    name: 'client',
    entry: './src/entrypoint.js',
    output: {
        filename: 'client.bundle.js',
        path: path.resolve('./dist')

    },
    mode: 'development',
    devtool: 'source-map',

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
                        // options: {
                        //     publicPath: 'dist/'
                        // }
                    }
                ],
            }
        ]
    },

    //optimization: {
    //    splitChunks: {
    //        cacheGroups: {
    //            styles: {
    //                name: 'style',
    //                test: /\.css$/,
    //                chunks: 'all',
    //                enforce: true
    //            }
    //        }
    //    }
    //},

    plugins: [
        //new MinifyPlugin(),
        new MiniCssExtractPlugin({
            filename: 'style.css',
        })
    ]
};

const serverConfig = {
    name: 'server',
    entry: './src/index.js',
    output: {
        filename: 'server.bundle.js',
        path: path.resolve('./dist'),
        libraryTarget: 'commonjs2',
    },
    mode: 'development',
    externals: [nodeExternals({
        whitelist: ['react', 'lodash'],
    })],

    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        forceEnv: 'node'
                    }
                }
            },
            {
                test: /\.css$/,
                use: 
                {
                    loader: 'ignore-loader'
                }
            },
        ]
    },


    plugins: [
        new CleanWebpackPlugin(['dist']),
        //new MinifyPlugin(),
        new MiniCssExtractPlugin({
            filename: '[name].css',
            allChuncks: true,
        })
    ]
};


const SSRServer = {
    name: 'SSRServer',
    entry: './render_server.js',
    output: {
        filename: 'render_server.bundle.js',
        path: path.resolve('./dist'),
        libraryTarget: 'commonjs2',
    },
    mode: 'production',
    target: 'node',
    externals: [nodeExternals()], 
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        forceEnv: 'node'
                    }
                }
            },
            {
                test: /\.css$/,
                use: 
                {
                    loader: 'ignore-loader'
                }
            },
        ]
    },


    plugins: [
        new CleanWebpackPlugin(['dist']),
        //new MinifyPlugin(),
        new MiniCssExtractPlugin({
            filename: '[name].css',
            allChuncks: true,
        })
    ]
};

module.exports = [clientConfig, serverConfig, SSRServer];
