# About

Reads a manifest file to import your assets into a Django template. Find
the URL for a single asset or the URLs for multiple assets by using
pattern matching against the file names. Path resolution handled using
Django's built-in ``staticfiles`` app. Minimal configuraton,
cache-busting, split chunks.

At its heart Django Manifest Loader is an extension to Django's built-in `static` template tag. 
When you use the provided `{% manifest %}` template tag, all the manifest loader is doing is 
taking the input string, looking it up against the manifest file, modifying the value, and then
passing along the result to the `{% static %}` template tag. The `{% manifest_match %}` tag works
similarly, just with a bit of additional logic to find all the necessary files and to render the output.


**Turns this**

```djangotemplate
{% load manifest %}
<script src="{% manifest 'main.js' %}" />
```

**Into this**

```djangotemplate
<script src="/static/main.8f7705adfa281590b8dd.js" />
```

* For an in-depth look at this package, check out [this blog post here](https://medium.com/@shonin/django-and-webpack-now-work-together-seamlessly-a90cffdbab8e)
* [Quick start guide](https://medium.com/@shonin/django-and-webpack-in-4-short-steps-b39bd3380c71)

## Additional resources

* [What is cache busting?](https://www.keycdn.com/support/what-is-cache-busting)
* [The 100% correct way to split your chunks with Webpack](https://medium.com/hackernoon/the-100-correct-way-to-split-your-chunks-with-webpack-f8a9df5b7758)

# Installation

```shell script
pip install django-manifest-loader
```


## Django Setup

```python
# settings.py

INSTALLED_APPS = [
    ...
    'manifest_loader',  # add to installed apps
    ...
]

STATICFILES_DIRS = [
    BASE_DIR / 'dist'  # the directory webpack outputs to
]
```

You must add webpack's output directory to the `STATICFILES_DIRS` list. 
The above example assumes that your webpack configuration is set up to output all files into a directory `dist/` that is 
in the `BASE_DIR` of your project.

`BASE_DIR`'s default value, as set by `$ djagno-admin startproject` is `BASE_DIR = Path(__file__).resolve().parent.parent`, in general 
you shouldn't be modifying it.

**Optional settings,** default values shown.
```python
# settings.py

MANIFEST_LOADER = {
    'output_dir': None,  # where webpack outputs to, if not set, will search in STATICFILES_DIRS for the manifest. 
    'manifest_file': 'manifest.json',  # name of your manifest file
    'cache': False,  # recommended True for production, requires a server restart to pick up new values from the manifest.
    'loader': DefaultLoader  # how the loader reading manifest files. 
}
```


## webpack configuration

_webpack is not technically required: Django Manifest Loader by default expects a manifest file in the form output by [webpack Manifest Plugin](https://github.com/shellscape/webpack-manifest-plugin). See the section on custom loaders for information on how to use a different type of manifest file._

You must install the `WebpackManifestPlugin`. Optionally, but recommended, is to install the `CleanWebpackPlugin`.

```shell script
npm i --save-dev webpack-manifest-plugin clean-webpack-plugin
```

```javascript
// webpack.config.js

const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');

module.exports = {
  ...
  plugins: [
      new CleanWebpackPlugin(),  // removes outdated assets from the output dir
      new ManifestPlugin(),  // generates the required manifest.json file
  ],
  ...
};
```


# Example Project Structure

```
BASE_DIR
├── dist  # webpack's output directory
│   ├── index.f82c02a005f7f383003c.js
│   └── manifest.json
├── frontend  # a django app
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