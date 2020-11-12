import json
import os
import fnmatch

from django import template
from django.templatetags.static import StaticNode
from django.conf import settings
from django.core.cache import cache
from django.utils.safestring import SafeString

from urllib.parse import quote


register = template.Library()

APP_SETTINGS = {
    'output_dir': None,
    'manifest_file': 'manifest.json',
    'cache': False,
    'ignore_missing_match_tag': False,
}

if hasattr(settings, 'MANIFEST_LOADER'):
    APP_SETTINGS.update(settings.MANIFEST_LOADER)


@register.tag('manifest')
def do_manifest(parser, token):
    return ManifestNode.handle_token(parser, token)


class ManifestNode(StaticNode):
    def render(self, context):
        if self.path.token[0] == self.path.token[-1] \
                and self.path.token[0] in ('"', "'"):
            manifest_key = self.path.token[1:-1]
        else:
            manifest_key = context.get(self.path.token)
            if not manifest_key:
                return super().render(context)

        manifest = get_manifest()
        manifest_value = manifest.get(manifest_key) if manifest.get(manifest_key) else manifest_key

        if manifest_value:
            self.path.var = SafeString(quote(manifest_value))
            self.path.token = '"{}"'.format(manifest_value)
        return super().render(context)


@register.tag('manifest_match')
def do_manifest_match(parser, token):
    return ManifestMatchNode(parser, token)


class ManifestMatchNode(template.Node):
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

        self.manifest = get_manifest()
        self.parser = parser
        self.token = token
        self.matched_files = [file for file in self.manifest.keys() if
                              fnmatch.fnmatch(file, self.search_string)]
        self.mapped_files = [self.manifest.get(file) for file in self.matched_files]

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


class WebpackManifestNotFound(Exception):
    def __init__(self, path, message='Manifest file named {} not found. '
                                     'Looked for it at {}. Either your '
                                     'settings are wrong or you still need to '
                                     'generate the file.'):
        super().__init__(message.format(APP_SETTINGS['manifest_file'], path))


class AssetNotFoundInWebpackManifest(Exception):
    def __init__(self, file, message='File {} is not referenced in the '
                                     'manifest file. Make '
                                     'sure webpack is outputting it or try '
                                     'disabling the cache if enabled. If '
                                     'you would like to suppress this '
                                     'error set MANIFEST_LOADER['
                                     '"ignore_missing_assets"] '
                                     'to True'):
        super().__init__(message.format(file))
