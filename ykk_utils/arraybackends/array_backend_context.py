from typing import Union

from .array_backend_base import ArrayBackendBase
from .array_backend_core import ArrayBackendManager

class ArrayBackendContext():
    def __init__(self,backend:Union[str,ArrayBackendManager,ArrayBackendBase]):
        self.backend:ArrayBackendBase = None

        if isinstance(backend,str):
            self.backend = ArrayBackendManager(backend).get_backend()
        elif isinstance(backend,ArrayBackendBase):
            self.backend = backend
        elif isinstance(backend,ArrayBackendManager):
            self.backend = backend.get_backend()
        else:
            raise Exception('backend is invalid')

    def __enter__(self):
        self.backend.reflist_init()
        return self.backend

    def __exit__(self, exc_type, exc, tb):
        self.backend.free_all()
        self.backend.reflist_deinit()
        return False
