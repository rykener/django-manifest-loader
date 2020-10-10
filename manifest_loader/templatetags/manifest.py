import json
import os

from django import template
from django.templatetags.static import do_static, StaticNode
from django.conf import settings
from django.core.cache import cache

from manifest_loader import loaders
from manifest_loader.exceptions import CustomManifestLoaderNotValid, \
    WebpackManifestNotFound, AssetNotFoundInWebpackManifest

register = template.Library()

APP_SETTINGS = {
    'output_dir': None,
    'manifest_file': 'manifest.json',
    'cache': False,
    'ignore_missing_assets': False,
    'ignore_missing_match_tag': False,
    'loader': loaders.DEFAULT
}

if hasattr(settings, 'MANIFEST_LOADER'):
    APP_SETTINGS.update(settings.MANIFEST_LOADER)


def load_from_manifest(filename=None, pattern=None):
    loader = APP_SETTINGS['loader']

    if not issubclass(loader, loaders.LoaderABC):
        raise CustomManifestLoaderNotValid

    manifest = get_manifest()

    if filename:
        return loader.get_single_match(manifest, filename)

    return loader.get_multi_match(manifest, pattern)


@register.tag('manifest')
def do_manifest(parser, token):
    try:
        tag_name, filename = parse_token(token)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag given the wrong number of arguments" %
            token.contents.split()[0]
        )

    hashed_filename = load_from_manifest(filename=filename)

    if hashed_filename:
        token.contents = "webpack '{}'".format(hashed_filename)
    elif not APP_SETTINGS['ignore_missing_assets']:
        raise AssetNotFoundInWebpackManifest(filename)

    return do_static(parser, token)


@register.tag('manifest_match')
def do_manifest_match(parser, token):
    return ManifestNode(parser, token)


class ManifestNode(template.Node):
    def __init__(self, parser, token):

        try:
            tag_name, self.search_string, self.output_tag = parse_token(token)
        except ValueError:
            raise template.TemplateSyntaxError(
                "%r tag given the wrong number of arguments" %
                token.contents.split()[0]
            )
        if '{match}' not in self.output_tag and not APP_SETTINGS['ignore_missing_match_tag']:
            raise template.TemplateSyntaxError(
                "manifest_match tag's second arg must contain the string {match}"
            )

        self.parser = parser
        self.token = token
        self.mapped_files = load_from_manifest(
                                pattern=self.search_string)

    def render(self, context):
        urls = []
        for file in self.mapped_files:
            self.token.contents = "manifest_match '{}'".format(file)
            node = StaticNode.handle_token(self.parser, self.token)
            url = node.render(context)
            urls.append(url)
        output_tags = [self.output_tag.format(match=file) for file in urls]
        return '\n'.join(output_tags)


def get_manifest():
    """
    looks in cache for manifest if caching enabled. If not found
    determines manifest location, opens file, and returns results
    as a dictionary
    """
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
    """searches settings.STATICFILES_DIRS for the manifest file"""
    static_dirs = settings.STATICFILES_DIRS
    if len(static_dirs) == 1:
        return os.path.join(static_dirs[0], APP_SETTINGS['manifest_file'])
    for static_dir in static_dirs:
        manifest_path = os.path.join(static_dir, APP_SETTINGS['manifest_file'])
        if os.path.isfile(manifest_path):
            return manifest_path
    raise WebpackManifestNotFound('settings.STATICFILES_DIRS')


def parse_token(token):
    contents = token.split_contents()
    if len(contents) == 2:
        tag_name, file_name = contents
        return tag_name, strip_quotes(tag_name, file_name)
    elif len(contents) == 3:
        tag_name, match_string, output_tag = contents
        return tag_name, strip_quotes(tag_name, match_string), strip_quotes(tag_name, output_tag)
    raise template.TemplateSyntaxError(
        "%r tag given the wrong number of arguments" % token.contents.split()[0]
    )


def strip_quotes(tag_name, content):
    """has test coverage"""
    if not isinstance(content, str):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be a string in quotes"
        )
    if not (content[0] == content[-1] and
            content[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )
    return content[1:-1]
