from django.conf import settings
from django.test import SimpleTestCase
from django.template import TemplateSyntaxError, Context, Template
from django.core.cache import cache
from django.apps import AppConfig

from manifest_loader.utils import _find_manifest_path, \
    _get_manifest, APP_SETTINGS, _is_quoted_string, _is_url

from manifest_loader.apps import ManifestLoader
from manifest_loader.exceptions import WebpackManifestNotFound, \
    CustomManifestLoaderNotValid
from manifest_loader.loaders import LoaderABC, DefaultLoader

NEW_STATICFILES_DIRS = [
    settings.BASE_DIR / 'foo',
    settings.BASE_DIR / 'bar' / 'baz',
    settings.BASE_DIR / 'dist',
    settings.BASE_DIR / 'bax',
]


def render_template(string, context=None):
    context = context or {}
    context = Context(context)
    return Template(string).render(context)


class IsUrlTests(SimpleTestCase):
    def test_is_url(self):
        self.assertTrue(_is_url('http://localhost:8080'))
        self.assertTrue(_is_url('https://localhost:8080'))
        self.assertTrue(_is_url('http://localhost'))
        self.assertTrue(_is_url('http://124.22.2.119:8080'))
        self.assertTrue(_is_url('https://example.com/static/main.js'))
        self.assertFalse(_is_url('main.hkl328o.js'))
        self.assertFalse(_is_url('http:hello.js'))
        self.assertFalse(_is_url('https.js'))


class IsQuotedStringTests(SimpleTestCase):
    def test_can_remove_quotes(self):
        self.assertTrue(_is_quoted_string('"foo"'))
        self.assertTrue(_is_quoted_string("'foo'"))
        self.assertFalse(_is_quoted_string("foo"))
        self.assertFalse(_is_quoted_string('foo'))
        self.assertFalse(_is_quoted_string('f'))


class FindManifestPathTests(SimpleTestCase):
    def test_default_path_found(self):
        self.assertEqual(
            str(settings.BASE_DIR / 'dist' / 'manifest.json'),
            _find_manifest_path()
        )

    def test_correct_path_found_among_options(self):
        with self.settings(STATICFILES_DIRS=NEW_STATICFILES_DIRS):
            self.assertEqual(len(settings.STATICFILES_DIRS), 4)
            self.assertEqual(
                str(settings.BASE_DIR / 'dist' / 'manifest.json'),
                _find_manifest_path()
            )

    def test_manifest_not_found(self):
        with self.settings(STATICFILES_DIRS=[settings.BASE_DIR / 'foo',
                                             settings.BASE_DIR / 'bar']):
            self.assertEqual(len(settings.STATICFILES_DIRS), 2)
            with self.assertRaises(WebpackManifestNotFound):
                _find_manifest_path()

    def test_manifest_not_found_empty(self):
        with self.settings(STATICFILES_DIRS=[]):
            self.assertEqual(len(settings.STATICFILES_DIRS), 0)
            with self.assertRaises(WebpackManifestNotFound):
                _find_manifest_path()


class GetManifestTests(SimpleTestCase):
    def test_cached_manifest(self):
        cache.set('webpack_manifest', {'foo': 'bar'})
        APP_SETTINGS.update({'cache': True})
        self.assertDictEqual(
            {'foo': 'bar'},
            _get_manifest()
        )
        cache.delete('webpack_manifest')
        APP_SETTINGS.update({'cache': False})

    def test_cache_not_used(self):
        cache.set('webpack_manifest', {'foo': 'bar'})
        self.assertFalse(APP_SETTINGS['cache'])
        self.assertDictEqual(
            {
                'main.js': 'main.e12dfe2f9b185dea03a4.js',
                "chunk1.js": "chunk1.hash.js",
                "chunk2.js": "chunk2.hash.js",
                "chunk3.js": "chunk3.hash.js",
                "styles.css": "styles.hash.css"
            },
            _get_manifest()
        )
        self.assertDictEqual(
            {'foo': 'bar'},
            cache.get('webpack_manifest')
        )
        cache.delete('webpack_manifest')

    def test_custom_output_dir(self):
        APP_SETTINGS.update({'output_dir': settings.BASE_DIR / 'foo'})
        with self.assertRaises(WebpackManifestNotFound):
            _get_manifest()
        APP_SETTINGS.update({'output_dir': None})

    def test_cache_set(self):
        APP_SETTINGS.update({'cache': True})
        self.assertIsNone(cache.get('webpack_manifest'))
        manifest = _get_manifest()

        self.assertDictEqual(
            manifest,
            {
                'main.js': 'main.e12dfe2f9b185dea03a4.js',
                "chunk1.js": "chunk1.hash.js",
                "chunk2.js": "chunk2.hash.js",
                "chunk3.js": "chunk3.hash.js",
                "styles.css": "styles.hash.css"
            },
        )

        self.assertDictEqual(
            manifest,
            cache.get('webpack_manifest')
        )
        APP_SETTINGS.update({'cache': False})
        cache.delete('webpack_manifest')


class ManifestTagTests(SimpleTestCase):
    def test_basic_usage(self):
        APP_SETTINGS.update({'manifest_file': 'manifest.json'})
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest "main.js" %}'
        )
        self.assertEqual(
            rendered,
            '/static/main.e12dfe2f9b185dea03a4.js'
        )

    def test_with_var_no_string(self):
        APP_SETTINGS.update({'manifest_file': 'manifest.json'})
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest foo %}',
            {'foo': 'main.js'}
        )
        self.assertEqual(
            rendered,
            '/static/main.e12dfe2f9b185dea03a4.js'
        )

    def test_with_undefined_var(self):
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest foo %}'
        )
        self.assertEqual(
            rendered,
            '/static/'
        )

    def test_non_default_static_url(self):
        APP_SETTINGS.update({'manifest_file': 'manifest.json'})
        with self.settings(STATIC_URL='/foo/'):
            rendered = render_template(
                '{% load manifest %}'
                '{% manifest "main.js" %}'
            )
            self.assertEqual(
                rendered,
                '/foo/main.e12dfe2f9b185dea03a4.js'
            )

    def test_no_arg(self):
        with self.assertRaises(TemplateSyntaxError):
            render_template(
                '{% load manifest %}'
                '{% manifest %}'
            )

    def test_missing_asset(self):
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest "foo.js" %}'
        )
        self.assertEqual(
            rendered,
            '/static/foo.js'
        )

    def test_url_in_manifest(self):
        APP_SETTINGS.update({'manifest_file': 'url_manifest.json'})
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest "main.js" %}'
        )
        self.assertEqual(
            rendered,
            'http://localhost:8080/main.js'
        )
        APP_SETTINGS.update({'manifest_file': 'manifest.json'})



class ManifestMatchTagTests(SimpleTestCase):
    def test_renders_correctly(self):
        APP_SETTINGS.update({'manifest_file': 'manifest.json'})
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest_match "*.css" "<foo {match} bar>" %}'
        )
        self.assertEqual(
            rendered,
            '<foo /static/styles.hash.css bar>'
        )

    def test_handles_no_math(self):
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest_match "*.exe" "<foo {match} bar>" %}'
        )
        self.assertEqual(
            rendered,
            ''
        )

    def test_renders_multiple_files(self):
        rendered = render_template(
            '{% load manifest %}'
            "{% manifest_match '*.js' '<script src=\"{match}\" />' %}"
        )
        self.assertEqual(
            rendered,
            '<script src="/static/main.e12dfe2f9b185dea03a4.js" />\n'
            '<script src="/static/chunk1.hash.js" />\n'
            '<script src="/static/chunk2.hash.js" />\n'
            '<script src="/static/chunk3.hash.js" />'
        )

    def test_ignores_missing_match_placeholder(self):
        rendered = render_template(
            '{% load manifest %}'
            "{% manifest_match '*.css' 'foo' %}"
        )
        self.assertEqual(
            rendered,
            'foo'
        )

    def test_handles_missing_arg(self):
        with self.assertRaises(TemplateSyntaxError):
            render_template(
                '{% load manifest %}'
                "{% manifest_match '*.css' %}"
            )

    def test_match_urls(self):
        APP_SETTINGS.update({'manifest_file': 'url_manifest.json'})
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest_match "*.js" "<script src=\"{match}\" />" %}'
        )
        self.assertEqual(
            rendered,
            '<script src="http://localhost:8080/main.js" />\n'
            '<script src="https://localhost:8080/chunk1.hash.js" />\n'
            '<script src="/static/chunk2.hash.js" />\n'
            '<script src="http://localhost:8080/chunk3.hash.js" />'
        )
        APP_SETTINGS.update({'manifest_file': 'manifest.json'})


class AppConfigTests(SimpleTestCase):
    def test_the_django_app(self):
        self.assertTrue(issubclass(ManifestLoader, AppConfig))


class LoadFromManifestTests(SimpleTestCase):
    def test_loader_not_subclass(self):
        class Foo:
            pass

        APP_SETTINGS.update({'loader': Foo})

        with self.assertRaises(CustomManifestLoaderNotValid):
            render_template(
                '{% load manifest %}'
                '{% manifest "main.js" %}'
            )

        APP_SETTINGS.update({'loader': DefaultLoader})


class LoaderABCTests(SimpleTestCase):
    def test_if_meta(self):
        self.assertTrue(hasattr(LoaderABC, 'register'))

    def test_methods_not_implemented(self):
        self.assertIsNone(LoaderABC.get_single_match('foo', 'bar'))
        self.assertIsNone(LoaderABC.get_multi_match('foo', 'bar'))
