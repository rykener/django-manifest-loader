from django.conf import settings
from django.test import SimpleTestCase
from django.template import TemplateSyntaxError
from django.core.cache import cache

from manifest_loader.templatetags.manifest import strip_quotes, \
    find_manifest_path, WebpackManifestNotFound, get_manifest, APP_SETTINGS

NEW_STATICFILES_DIRS = [
    settings.BASE_DIR / 'foo',
    settings.BASE_DIR / 'bar' / 'baz',
    settings.BASE_DIR / 'dist',
    settings.BASE_DIR / 'bax',
]


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
            {'main.js': 'main.e12dfe2f9b185dea03a4.js'},
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
            {'main.js': 'main.e12dfe2f9b185dea03a4.js'}
        )

        self.assertDictEqual(
            manifest,
            cache.get('webpack_manifest')
        )
        APP_SETTINGS.update({'cache': False})
        cache.delete('webpack_manifest')
