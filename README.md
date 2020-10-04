# Easy Django webpack

_Always have access to the latest assets, with minimal configuration. Wraps Django's built in 
`{% static %}` templatetag to allow you to link to assets according to a webpack manifest file._

## Installation

```shell script
pip install easy_django_webpack
```

## Setup

```python
# settings.py

INSTALLED_APPS = [
    ...
    'easy_django_webpack',
    ...
]
```

You must add webpack's output directory to the `STATICFILES_DIRS` list. 
If your webpack configuration is to output all files into a directory `dist/` that is 
in the `BASE_DIR` of your project, then you would set it like. 

```python
# settings.py
STATICFILES_DIRS = [
    BASE_DIR / 'dist'
]
```

`BASE_DIR`'s default value is `BASE_DIR = Path(__file__).resolve().parent.parent`, in general 
you shouldn't be modifying it. _Hint: the `BASE_DIR` is the directory your `manage.py` file is in._

**Optional settings,** default values shown.
```python
# settings.py

WEBPACK_SETTINGS = {
    'output_dir': BASE_DIR / 'dist',  # where webpack outputs to. 
    'manifest_file': 'manifest.json',  # name of your manifest file
    'cache': False  # recommended `True` for production, requires a server restart to pickup new values from the manifest.
}
```

## Webpack example

Install webpack:

```shell script
npm i --save-dev webpack webpack-cli
```

Install recommended plugins
```shell script
npm i --save-dev webpack-manifest-plugin clean-webpack-plugin
```

```javascript
// webpack.config.js

const path = require('path');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');

module.exports = {
  entry: './frontend/src/index.js',
  plugins: [
      new CleanWebpackPlugin(),  // removes outdated assets from the output dir
      new ManifestPlugin(),  // generates the required manifest.json file
  ],
  output: {
    filename: '[name].[contenthash].js',  // renames files from example.js to example.8f77someHash8adfa.js
    path: path.resolve(__dirname, 'dist'),
  },
};
```

```javascript
// package.json
...
"scripts": {
  "start": "webpack"
},
...
```

## Usage

```djangotemplate
{% load webpack %}

<script src="{% manifest 'main.js' %}"></script>
```

turns into

```html
<script src="/static/main.8f7705adfa281590b8dd.js"></script>
```