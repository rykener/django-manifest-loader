from django.conf import settings
from django.test import SimpleTestCase
from django.template import TemplateSyntaxError, Context, Template
from django.core.cache import cache

from manifest_loader.templatetags.manifest import strip_quotes, \
    find_manifest_path, WebpackManifestNotFound, get_manifest, APP_SETTINGS, \
    AssetNotFoundInWebpackManifest


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


class StripQuotesTests(SimpleTestCase):
    def test_can_remove_quotes(self):
        self.assertEqual(
            strip_quotes('test_case', "'foobar'"),
            'foobar'
        )
        self.assertEqual(
            strip_quotes('test_case', '"foobar"'),
            'foobar'
        )

    def test_will_raise_exception(self):
        with self.assertRaises(TemplateSyntaxError):
            strip_quotes('test_case', 'foobar')
        with self.assertRaises(TemplateSyntaxError):
            strip_quotes('test_case', 'foobar"')
        with self.assertRaises(TemplateSyntaxError):
            strip_quotes('test_case', 1234)
        with self.assertRaises(TemplateSyntaxError):
            strip_quotes('test_case', {'doo': 'bar'})


class FindManifestPathTests(SimpleTestCase):
    def test_default_path_found(self):
        self.assertEqual(
            str(settings.BASE_DIR / 'dist' / 'manifest.json'),
            find_manifest_path()
        )

    def test_correct_path_found_among_options(self):
        with self.settings(STATICFILES_DIRS=NEW_STATICFILES_DIRS):
            self.assertEqual(len(settings.STATICFILES_DIRS), 4)
            self.assertEqual(
                str(settings.BASE_DIR / 'dist' / 'manifest.json'),
                find_manifest_path()
            )

    def test_manifest_not_found(self):
        with self.settings(STATICFILES_DIRS=[settings.BASE_DIR / 'foo',
                                             settings.BASE_DIR / 'bar']):
            self.assertEqual(len(settings.STATICFILES_DIRS), 2)
            with self.assertRaises(WebpackManifestNotFound):
                find_manifest_path()

    def test_manifest_not_found_empty(self):
        with self.settings(STATICFILES_DIRS=[]):
            self.assertEqual(len(settings.STATICFILES_DIRS), 0)
            with self.assertRaises(WebpackManifestNotFound):
                find_manifest_path()


class GetManifestTests(SimpleTestCase):
    def test_cached_manifest(self):
        cache.set('webpack_manifest', {'foo': 'bar'})
        APP_SETTINGS.update({'cache': True})
        self.assertDictEqual(
            {'foo': 'bar'},
            get_manifest()
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
            get_manifest()
        )
        self.assertDictEqual(
            {'foo': 'bar'},
            cache.get('webpack_manifest')
        )
        cache.delete('webpack_manifest')

    def test_custom_output_dir(self):
        APP_SETTINGS.update({'output_dir': settings.BASE_DIR / 'foo'})
        with self.assertRaises(WebpackManifestNotFound):
            get_manifest()
        APP_SETTINGS.update({'output_dir': None})

    def test_cache_set(self):
        APP_SETTINGS.update({'cache': True})
        self.assertIsNone(cache.get('webpack_manifest'))
        manifest = get_manifest()

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
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest "main.js" %}'
        )
        self.assertEqual(
            rendered,
            '/static/main.e12dfe2f9b185dea03a4.js'
        )

    def test_non_default_static_url(self):
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

    def test_too_many_args(self):
        with self.assertRaises(TemplateSyntaxError):
            render_template(
                '{% load manifest %}'
                '{% manifest "foo" "bar" %}'
            )

    def test_missing_asset(self):
        with self.assertRaises(AssetNotFoundInWebpackManifest):
            render_template(
                '{% load manifest %}'
                '{% manifest "foo.js" %}'
            )

    def test_ignore_missing_assets(self):
        APP_SETTINGS.update({'ignore_missing_assets': True})
        rendered = render_template(
            '{% load manifest %}'
            '{% manifest "foo.js" %}'
        )
        self.assertEqual(
            rendered,
            '/static/foo.js'
        )
        APP_SETTINGS.update({'ignore_missing_assets': False})


class ManifestMatchTagTests(SimpleTestCase):
    def test_renders_correctly(self):
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

    def test_handles_missing_match_placeholder(self):
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
