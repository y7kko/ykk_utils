from .array_backend_base import ArrayBackendBase
from .array_backend_core import array_backend, ArrayBackendManager,keep_reference

from .numpy_backend import numpy_backend
try:
    from .cupy_backend import cupy_backend
except:
    pass

from .array_backend_context import ArrayBackendContext
from .array_slicetools import arr_split2d, cross_slice2d
