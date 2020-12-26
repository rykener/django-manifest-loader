import json
import os
import fnmatch

from django import template
from django.templatetags.static import StaticNode
from django.conf import settings
from django.core.cache import cache
from django.utils.html import conditional_escape
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


from manifest_loader.exceptions import WebpackManifestNotFound


register = template.Library()

APP_SETTINGS = {
    'output_dir': None,
    'manifest_file': 'manifest.json',
    'cache': False
}

if hasattr(settings, 'MANIFEST_LOADER'):
    APP_SETTINGS.update(settings.MANIFEST_LOADER)


@register.tag('manifest')
def do_manifest(parser, token): 
    """Returns the manifest tag """
    return ManifestNode(token)

@register.tag('manifest_match')
def do_manifest_match(parser, token):
    """Returns manifest match tag"""
    return ManifestMatchNode(token)



class ManifestNode(template.Node):
    """ Initalizes the creation of the manifest template tag"""
    def __init__(self, token):
        bits = token.split_contents()
        if len(bits) < 2:
            raise template.TemplateSyntaxError(
                "'%s' takes one argument (name of file)" % bits[0])
        self.bits = bits


    def render(self, context):
        """Renders the creation of the manifest tag"""
        manifest_key = get_value(self.bits[1], context)
        manifest = get_manifest()
        manifest_value = manifest.get(manifest_key, manifest_key)
        return make_url(manifest_value, context)


class ManifestMatchNode(template.Node):
    """ Initalizes the creation of the manifest match template tag"""
    def __init__(self, token):
        self.bits = token.split_contents()
        if len(self.bits) < 3:
            raise template.TemplateSyntaxError(
                "'%s' takes two arguments (pattern to match and string to "
                "insert into)" % self.bits[0]
            )

    def render(self, context):
        """ Renders the manifest match tag"""
        urls = []
        search_string = get_value(self.bits[1], context)
        output_tag = get_value(self.bits[2], context)

        manifest = get_manifest()

        matched_files = [file for file in manifest.keys() if
                         fnmatch.fnmatch(file, search_string)]
        mapped_files = [manifest.get(file) for file in matched_files]

        for file in mapped_files:
            url = make_url(file, context)
            urls.append(url)
        output_tags = [output_tag.format(match=file) for file in urls]
        return '\n'.join(output_tags)


def get_manifest():
    """ Returns the manifest file from the output directory """
    cached_manifest = cache.get('webpack_manifest')
    if APP_SETTINGS['cache'] and cached_manifest:
        return cached_manifest

    if APP_SETTINGS['output_dir']:
        manifest_path = os.path.join(APP_SETTINGS['output_dir'],
                                     APP_SETTINGS['manifest_file'])
    else:
        manifest_path = find_manifest_path()

    try:
        with open(manifest_path) as manifest_file:
            data = json.load(manifest_file)
    except FileNotFoundError:
        raise WebpackManifestNotFound(manifest_path)

    if APP_SETTINGS['cache']:
        cache.set('webpack_manifest', data)

    return data


def find_manifest_path():
    """ Returns manifest_file """
    static_dirs = settings.STATICFILES_DIRS
    if len(static_dirs) == 1:
        return os.path.join(static_dirs[0], APP_SETTINGS['manifest_file'])
    for static_dir in static_dirs:
        manifest_path = os.path.join(static_dir, APP_SETTINGS['manifest_file'])
        if os.path.isfile(manifest_path):
            return manifest_path
    raise WebpackManifestNotFound('settings.STATICFILES_DIRS')


def is_quoted_string(string):
    """Method validates if it's a stirng"""
    if len(string) < 2:
        return False
    return string[0] == string[-1] and string[0] in ('"', "'")


def get_value(string, context):
    """Method validates the value of the string"""
    if is_quoted_string(string):
        return string[1:-1]
    return context.get(string, '')


def is_url(potential_url):
    """Function validates if it's a URL """
   
    validate = URLValidator()
    try:
        validate(potential_url)
        return True
    except ValidationError:
        return False


def make_url(manifest_value, context):
    """ Returns the URL that will be outputed to the static file directory"""

    if is_url(manifest_value):
        url = manifest_value
    else:
        url = StaticNode.handle_simple(manifest_value)
    if context.autoescape:
        url = conditional_escape(url)
    return url
