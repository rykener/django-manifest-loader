import json
import os

from django import template
from django.templatetags.static import do_static
from django.conf import settings
from django.core.cache import cache

register = template.Library()

APP_SETTINGS = {
    'output_dir': settings.BASE_DIR / 'dist',
    'manifest_file': 'manifest.json',
    'cache': False
}

if hasattr(settings, 'WEBPACK_SETTINGS'):
    APP_SETTINGS.update(settings.WEBPACK_SETTINGS)


@register.tag('manifest')
def manifest(parser, token):
    cached_manifest = cache.get('webpack_manifest')

    if APP_SETTINGS['cache'] and cached_manifest:
        data = cached_manifest
    else:
        path = os.path.join(APP_SETTINGS['output_dir'],
                            APP_SETTINGS['manifest_file'])

        try:
            with open(path) as manifest_file:
                data = json.load(manifest_file)
        except FileNotFoundError:
            raise WebpackManifestNotFound(path)

        if APP_SETTINGS['cache']:
            cache.set('webpack_manifest', data)

    token.contents = "webpack '{}'".format(data.get(parse_filename(token)))

    return do_static(parser, token)


def parse_filename(token):
    return token.contents.split("'")[1]


class WebpackManifestNotFound(Exception):
    def __init__(self, path, message='Manifest file named {} not found. '
                                     'Looked for it at {}. Either your '
                                     'settings are wrong or you need to still '
                                     'generate the file.'):
        super().__init__(message.format(APP_SETTINGS['manifest_file'], path))
