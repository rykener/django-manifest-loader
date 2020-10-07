# Django Manifest Loader

[![Build Status](https://travis-ci.org/shonin/django-manifest-loader.png?branch=dev)](https://travis-ci.org/shonin/django-manifest-loader)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](#)

_Always have access to the latest assets, with minimal configuration. Wraps Django's built in 
`{% static %}` templatetag to allow you to link to assets according to a webpack manifest file._

**Turns this**

```djangotemplate
{% load manifest %}
<script src="{% manifest 'main.js' %}" />
```

**Into this**

```djangotemplate
<script src="/static/main.8f7705adfa281590b8dd.js" />
```

## Installation

```shell script
pip install django_manifest_loader
```

## Setup

```python
# settings.py

INSTALLED_APPS = [
    ...
    'manifest_loader',
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

MANIFEST_LOADER = {
    'output_dir': BASE_DIR / 'dist',  # where webpack outputs to. 
    'manifest_file': 'manifest.json',  # name of your manifest file
    'cache': False,  # recommended True for production, requires a server restart to pickup new values from the manifest.
    'ignore_missing_assets': False  # recommended True for production. Otherwise raises an exception if a file is not in the manifest.
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
    path: path.resolve(__dirname, 'dist'), // output to BASE_DIR/dist, assumes webpack.json is on the same level as manage.py
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
{% load manifest %}

<script src="{% manifest 'main.js' %}"></script>
```

turns into

```html
<script src="/static/main.8f7705adfa281590b8dd.js"></script>
```

## About

At it's heart Django Manifest Loader is an extension to Django's built-in `static` templatetag. 
When you use the provided `{% manifest %}` templatetag, all the manifest loader is doing is 
taking the input string, looking it up against the manifest file, modifying the value, and then
passing along the result to the `{% static %}` template tag. 

### Suggested Project Structure

```
BASE_DIR
├── dist
│   ├── main.f82c02a005f7f383003c.js
│   └── manifest.json
├── frontend
│   ├── apps.py
│   ├── src
│   │   └── index.js
│   ├── templates
│   │   └── frontend
│   │       └── index.html
│   └── views.py
├── manage.py
├── package.json
├── project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── requirements.txt
└── webpack.config.js
```

### Manifest File and Content Hash (the problem this package solves)

When you put a content hash in the filename of an asset file, it serves as a sort of versioning mechanism
for your assets. Every time the content changes, the hash changes. And when the hash changes, the browser sees that it 
doesn't have that asset file, it drops it's 
cached version of your old assets and gets the new one. If you only use the name `main.js` for your assets, the browser
will just think, oh hey I have this file in my cache, and it won't check for updates. So then your users 
won't see the latest changes unless they do a browser cache refresh, which isn't something you can expect.

So you can see why you want the content hash in the filename. The manifest.json file is a way to provide a mapping
from the original file name to the new one. If you didn't have a way to automate that mapping, every time you generate
a new version of your assets, you'd have to go into your HTML and update the content hash yourself. Instead, you
can just tell Django Manifest Loader that you want the file `main.js` and it'll lookup the content hash for you. 

### License 

Django Manifest Loader is distributed under the [3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause). 
This is an open source license granting broad permissions to modify and redistribute the software.
