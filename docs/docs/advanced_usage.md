# Custom Loaders

## Writing a custom loader

Custom loaders allow you to implement your own means of extracting data from your manifest file. If your manifest
file is not the default structure of [webpack manifest plugin](https://github.com/shellscape/webpack-manifest-plugin), this is how you can tell `django-manifest-loader` how to read it.

First import the loader parent abstract class, and subclass it in your new loader class. 

```python
from manifest_loader.loaders import LoaderABC

class MyCustomLoader(LoaderABC):
```

Your new loader must have two static methods that each take two required arguments: 
`get_single_match(manifest, key)` and `get_multi_match(manifest, pattern)`.

```python
from manifest_loader.loaders import LoaderABC

class MyCustomLoader(LoaderABC):
    @staticmethod
    def get_single_match(manifest, key):
        pass

    @staticmethod
    def get_multi_match(manifest, pattern):
        pass
```

* `get_single_match` - returns a `String`, finds a single file in your manifest file, according to the `key`
* `get_multi_match` - returns a `List` of files in your manifest, according to the `pattern`
* `manifest` - this is your full manifest file, after being processed by `json.load()`. It will be a dictionary or list
    depending on which it is in your manifest file. 
* `key` - `String`; the argument passed into the `manifest` template tag. e.g.: in the template tag `{% manifest 'index.js' %}`, 
    the string `'index.js'` is sent to `get_single_match` as `key` (without surrounding quotes)
* `pattern` - `String`; the first argument passed into the `manifest_match` template tag. e.g.: in the template tag 
    `{% manifest_match '*.js' '<script src="{match}"></script>' %}`, the string `'*.js'` is sent to `get_multi_match` 
    as `pattern` (without surrounding quotes)
    
**Below is the code for the default loader, which is a good starting point:**

```python
import fnmatch
from manifest_loader.loaders import LoaderABC

class DefaultLoader(LoaderABC):
    @staticmethod
    def get_single_match(manifest, key):
        return manifest.get(key, key)

    @staticmethod
    def get_multi_match(manifest, pattern):
        matched_files = [file for file in manifest.keys() if
                         fnmatch.fnmatch(file, pattern)]
        return [manifest.get(file) for file in matched_files]
``` 

In the above example, `get_single_match` retrieves the value on the `manifest` dictionary that matches the key `key`. If
the key does not exist on the dictionary, it instead returns the key.

`get_multi_match` uses the recommended `fnmatch` python standard library to do pattern matching. You could also use 
regex in it's place. Here, it iterates through all the keys in the manifest file, and builds a list of the keys that 
match the given `pattern`. It then returns a list of the values associated with those matched keys. 

## Activating the custom loader 

To put the custom loader into use it needs to be registered in your `settings.py`.

```python
# settings.py
from my_app.utils import MyCustomLoader

MANIFEST_LOADER = {
    ...
    'loader': MyCustomLoader
}
```

## Contribute your custom loader

If you write a custom loader that you think would be helpful for others, or if you have a specific loader request, please either make a pull request or file an issue in this [project's Github](https://github.com/shonin/django-manifest-loader).

# URLs in Manifest File

If your manifest file points to full URLs, instead of file names, the full URL will be output instead of pointing to the static file directory in Django.

Example:

```json
{
  "main.js": "http://localhost:8080/main.js"
}
```

```html
{% load manifest %}

<script src="{% manifest 'main.js' %}"></script>
```

Will output as:

```html
<script src="http://localhost:8080/main.js"></script>
```


# Tests and Code Coverage

Run unit tests and verify 100% code coverage with:

```
git clone https://github.com/shonin/django-manifest-loader.git
cd django-manifest-loader
pip install -e .

# run tests
python runtests.py

# check code coverage
pip install coverage
coverage run --source=manifest_loader/ runtests.py
coverage report
```
