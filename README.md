# Django Manifest Loader 

[![Build Status](https://img.shields.io/travis/shonin/django-manifest-loader/main?label=stable%20branch&style=flat-square
)](https://travis-ci.org/shonin/django-manifest-loader)
[![Build Status](https://img.shields.io/travis/shonin/django-manifest-loader/dev?label=development%20branch&style=flat-square
)](https://travis-ci.org/shonin/django-manifest-loader)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat-square)](#)


Reads a manifest file to import your assets into a Django template. Find
the URL for a single asset or the URLs for multiple assets by using
pattern matching against the file names. Path resolution handled using
Django's built-in `staticfiles` app. Minimal configuraton,
cache-busting, split chunks.

## [Documentation](https://django-manifest-loader.readthedocs.io/en/latest/index.html)

## About

**Turns this**

```djangotemplate
{% load manifest %}
<script src="{% manifest 'main.js' %}"></script>
```

**Into this**

```djangotemplate
<script src="/static/main.8f7705adfa281590b8dd.js"></script>
```

* [Official documentation](https://django-manifest-loader.readthedocs.io/en/latest/index.html)
* For an in-depth look at this package, check out [this blog post here](https://medium.com/@shonin/django-and-webpack-now-work-together-seamlessly-a90cffdbab8e)
* [Quick start blog post](https://medium.com/@shonin/django-and-webpack-in-4-short-steps-b39bd3380c71)

## Quick reference:

### Manifest tag

```djangotemplate
{% load manifest %}

<script src="{% manifest 'main.js' %}"></script>
```

turns into

```html
<script src="/static/main.8f7705adfa281590b8dd.js"></script>
```

### Manifest match tag

```djangotemplate
{% load manifest %}

{% manifest_match '*.js' '<script src="{match}"></script>' %}
```

turns into

```html
<script src="/static/vendors~main.3ad032adfa281590f2a21.js"></script>
<script src="/static/main.8f7705adfa281590b8dd.js"></script>
```

### License 

Django Manifest Loader is distributed under the [3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause). 
This is an open source license granting broad permissions to modify and redistribute the software.

