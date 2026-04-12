from django.core.files.base import ContentFile
from django.core.files.storage import Storage


class TestMemoryStorage(Storage):
    _files = {}

    @classmethod
    def clear(cls):
        cls._files = {}

    def _open(self, name, mode='rb'):
        stored_file = ContentFile(self._files[name])
        stored_file.name = name
        return stored_file

    def _save(self, name, content):
        if hasattr(content, 'seek'):
            content.seek(0)
        self._files[name] = content.read()
        return name

    def exists(self, name):
        return name in self._files

    def delete(self, name):
        self._files.pop(name, None)

    def size(self, name):
        return len(self._files[name])

    def url(self, name):
        return f'/media/{name}'
