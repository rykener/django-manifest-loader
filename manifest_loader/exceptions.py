class CustomManifestLoaderNotValid(Exception):
    def __init__(self, message='Custom manifest loader defined in settings.py '
                               'must inherit from '
                               'manifest_loader.loaders.LoaderABC'):
        super().__init__(message)


class WebpackManifestNotFound(Exception):
    def __init__(self, path, message='Manifest file not found. '
                                     'Looked for it at {}. Either your '
                                     'settings are wrong or you still need to '
                                     'generate the file.'):
        super().__init__(message.format(path))


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
