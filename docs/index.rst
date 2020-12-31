Django Manifest Loader
=========================

| |Stable Status| |Dev Status| |contributions welcome|

Django Manifest Loader reads a manifest file to import your assets into a Django template. Find
the URL for a single asset OR find the URLs for multiple assets by using
pattern matching against the file names. Path resolution handled using
Django's built-in ``staticfiles`` app. Minimal configuraton, cache-busting, split chunks.
Designed for webpack, ready for anything. 

.. toctree::
   :maxdepth: 2

   docs/about_install
   docs/usage
   docs/loaders
   docs/advanced_usage
   docs/philosophy
   docs/reference
   docs/docs_license

.. |Stable Status| image:: https://img.shields.io/travis/shonin/django-manifest-loader/main?label=stable%20branch&style=flat-square
   :target: https://travis-ci.org/shonin/django-manifest-loader
.. |Dev Status| image:: https://img.shields.io/travis/shonin/django-manifest-loader/dev?label=development%20branch&style=flat-square
   :target: https://travis-ci.org/shonin/django-manifest-loader
.. |contributions welcome| image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat-square
   :target: #
