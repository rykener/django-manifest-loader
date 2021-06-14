from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class DjangoManifestLoaderStorage(ManifestStaticFilesStorage):
    """
    If a file isn’t found in the staticfiles.json manifest at runtime, don't raise an exception
    """
    manifest_strict = False
