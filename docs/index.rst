Django Manifest Loader
=========================

| |Stable Status| |Dev Status| |contributions welcome|

Reads a manifest file to import your assets into a Django template. Find
the URL for a single asset, or the URLs for multiple assets by using
pattern matching against the file names. Path resolution handled using
Django's built-in ``staticfiles`` app. Minimal configuraton,
cache-busting, split chunks.

.. toctree::
   :maxdepth: 1

   docs/about_install
   docs/usage
   docs/reference
   docs/docs_license

.. |Stable Status| image:: https://img.shields.io/travis/shonin/django-manifest-loader/main?label=latest%20published%20branch&style=flat-square
   :target: https://travis-ci.org/shonin/django-manifest-loader
.. |Dev Status| image:: https://img.shields.io/travis/shonin/django-manifest-loader/dev?label=development%20branch&style=flat-square
   :target: https://travis-ci.org/shonin/django-manifest-loader
.. |contributions welcome| image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat-square
   :target: #
