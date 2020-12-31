const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const { WebpackManifestPlugin } = require('webpack-manifest-plugin');

module.exports = {
  entry: './frontend/src/index.js',
  plugins: [
      new CleanWebpackPlugin(),  // removes outdated assets from the output dir
      new WebpackManifestPlugin(),  // generates the required manifest.json file
  ],
  output: {
      publicPath: '',
    filename: '[name].[contenthash].js',  // renames files from example.js to example.8f77someHash8adfa.js
    path: path.resolve(__dirname, 'dist'),
  },
};