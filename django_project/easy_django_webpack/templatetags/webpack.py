import json
import os

from django import template
from django.templatetags.static import do_static
from django.conf import settings

register = template.Library()

APP_SETTINGS = {
    'output_dir': settings.BASE_DIR / 'dist',
    'manifest_file': 'manifest.json',
    'cache': False
}

if hasattr(settings, 'WEBPACK_SETTINGS'):
    APP_SETTINGS.update(settings.WEBPACK_SETTINGS)


@register.tag('static')
def webpack(parser, token):
    return do_static(parser, token)


@register.tag('manifest')
def webpack(parser, token):
    path = os.path.join(APP_SETTINGS['output_dir'],
                        APP_SETTINGS['manifest_file'])

    with open(path) as manifest:
        data = json.load(manifest)

    token.contents = "webpack '{}'".format(data.get(parse_filename(token)))

    return do_static(parser, token)


def parse_filename(token):
    return token.contents.split("'")[1]