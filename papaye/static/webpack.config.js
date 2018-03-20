const path = require('path');

module.exports = {
  entry: "./src/index.js", // string | object | array
  output: {
    filename: 'bundle.js',
    path: path.resolve('./dist')

  },
  mode: "development",
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
      }
    ]
  }
}
