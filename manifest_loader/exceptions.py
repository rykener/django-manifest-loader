class WebpackManifestNotFound(Exception):
    def __init__(self, path, message='Manifest file not found. '
                                     'Looked for it at {}. Either your '
                                     'settings are wrong or you still need to '
                                     'generate the file.'):
        super().__init__(message.format(path))


class CustomManifestLoaderNotValid(Exception):
    def __init__(self, message='Custom manifest loader defined in settings.py '
                               'must inherit from '
                               'manifest_loader.loaders.LoaderABC'):
        super().__init__(message)
