class WebpackManifestNotFound(Exception):
    def __init__(self, path, message='Manifest file not found. '
                                     'Looked for it at {}. Either your '
                                     'settings are wrong or you still need to '
                                     'generate the file.'):
        super().__init__(message.format(path))
