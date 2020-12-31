import fnmatch
from abc import ABCMeta, abstractmethod


class LoaderABC(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def get_single_match(manifest, key):
        pass

    @staticmethod
    @abstractmethod
    def get_multi_match(manifest, pattern):
        pass


class DefaultLoader(LoaderABC):
    @staticmethod
    def get_single_match(manifest, key):
        return manifest.get(key, key)

    @staticmethod
    def get_multi_match(manifest, pattern):
        matched_files = [file for file in manifest.keys() if
                         fnmatch.fnmatch(file, pattern)]
        return [manifest.get(file) for file in matched_files]


class CreateReactAppLoader(LoaderABC):
    @staticmethod
    def get_single_match(manifest, key):
        files = manifest.get('files', {})
        return files.get(key, key)

    @staticmethod
    def get_multi_match(manifest, pattern):
        split_pattern = pattern.split(' ')
        parent = split_pattern[0] if len(split_pattern) == 2 else 'entrypoints'
        pattern = split_pattern[1] if len(split_pattern) == 2 else split_pattern[0]
        files = manifest.get(parent, {})

        if isinstance(files, dict):
            matched_files = [file for file in files.keys() if
                         fnmatch.fnmatch(file, pattern)]
            return [files.get(file) for file in matched_files]

        elif isinstance(files, list):
            return [file for file in files if fnmatch.fnmatch(file, pattern)]

        return []

