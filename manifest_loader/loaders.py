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