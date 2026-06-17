
from .array_backend_core import array_backend,keep_reference
from .array_backend_base import ArrayBackendBase

import cupy as cp
import numpy as np
from scipy.signal import savgol_coeffs
from cupyx.scipy import ndimage
from cupyx import linalg

from functools import wraps

@array_backend('cupy')
class cupy_backend(ArrayBackendBase):
    """
        https://docs.cupy.dev/en/v9.6.0/reference/index.html

    """
    @keep_reference
    @wraps(cp.asarray)
    def to_backend(cls,arr,**kwargs):
        arr_out = cp.asarray(arr,**kwargs)
        return arr_out 

    @wraps(cp.asnumpy)
    def to_numpy(arr,**kwargs):
        return cp.asnumpy(arr,**kwargs)
    
    @wraps(cp.fft.rfft)
    @keep_reference
    def rfft(cls,*args,**kwargs):
        return cp.fft.rfft(*args,**kwargs)
    
    @wraps(cp.fft.irfft)
    @keep_reference
    def irfft(cls,*args,**kwargs):
        return cp.fft.irfft(*args,**kwargs)
    
    @keep_reference
    def norm_max(cls,input:cp.ndarray,axis=-1):
        #maybe, declarar uma classe Protocol com documentacao
        return input / abs(input).max(axis=axis,keepdims=True)

    @keep_reference
    def lstsq(cls,*args,**kwargs):
        return cp.linalg.lstsq(*args,**kwargs)


    @classmethod
    def free_mem(cls,arr:cp.ndarray):
        arr.data.mem.free()
        cls.reflist_remove(arr)

    @classmethod
    def free_all(cls,):
        cls.reflist_deinit()
        cp.get_default_memory_pool().free_all_blocks()
