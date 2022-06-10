from os import path
from setuptools import setup, find_packages


readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.md')

try:
    from m2r import parse_from_file
    long_description = parse_from_file(readme_file)     # Convert the file to RST for PyPI
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        long_description = f.read()


package_metadata = {
    'name': 'django-manifest-loader',
    'version': "1.0.1",
    'description': 'A Django app to load webpack assets.',
    'long_description': 'A Django app to load webpack assets.',
    'url': 'https://github.com/WhiteMoonDreamsInc/django-manifest-loader/',
    'author': 'Shonin',
    'author_email': 'emc@hey.com',
    'license': 'BSD-3-Clause',
    'classifiers': [
        'Environment :: Web Environment'
        'Framework :: Django'
        'Framework :: Django :: 3.1'
        'Intended Audience :: Developers'
        'License :: OSI Approved :: BSD License'
        'Operating System :: OS Independent'
        'Programming Language :: Python'
        'Programming Language :: Python :: 3'
        'Programming Language :: Python :: 3 :: Only'
        'Programming Language :: Python :: 3.6'
        'Programming Language :: Python :: 3.7'
        'Programming Language :: Python :: 3.8'
        'Topic :: Internet :: WWW/HTTP'
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
    'keywords': ['django', 'webpack', 'manifest', 'loader'],
}

setup(
    packages=find_packages(),
    package_data={'manifest_loader': ['templatetags/*']},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        'Django>=3.0,<4.0',
    ],
    extras_require={
        'test': [],
        'prod': [],
        'build': [
            'setuptools',
            'wheel',
            'twine',
            'm2r',
        ],
        'docs': [
            'recommonmark',
            'm2r',
            'django_extensions',
            'coverage',
            'Sphinx',
            'rstcheck',
            'sphinx-rtd-theme'
        ],
    },
    **package_metadata
)