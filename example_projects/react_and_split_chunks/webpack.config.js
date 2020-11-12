const path = require('path');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');

module.exports = {
  entry: './frontend/src/app.js',
  plugins: [
      new CleanWebpackPlugin(),  // removes outdated assets from the output dir
      new ManifestPlugin(),  // generates the required manifest.json file
  ],
  module: {
  	rules: [
	  	{
	        test: /\.js$/,
	        exclude: /node_modules/,
	        use: {
	            loader: "babel-loader"
	        }
	    },
	  ],
	},
  output: {
    filename: '[name].[contenthash].js',  // renames files from example.js to example.8f77someHash8adfa.js
    path: path.resolve(__dirname, 'dist'), // output to BASE_DIR/dist, assumes webpack.json is on the same level as manage.py
  },
  optimization: {
    runtimeChunk: 'single',
    splitChunks: {
      chunks: 'all',
      maxInitialRequests: Infinity,
      minSize: 0,
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name(module) {
            // get the name. E.g. node_modules/packageName/not/this/part.js
            // or node_modules/packageName
            const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];

            // npm package names are URL-safe, but some servers don't like @ symbols
            return `npm.${packageName.replace('@', '')}`;
          },
        },
      },
    },
  },
};