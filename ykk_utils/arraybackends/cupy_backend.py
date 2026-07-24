import warnings

from .array_backend_core import array_backend,keep_reference
from .array_backend_base import ArrayBackendBase

from scipy.signal import savgol_coeffs


import cupy as cp
import cupyx.scipy as scp
from cupyx.scipy.signal import fftconvolve
from cupyx.scipy import ndimage
from cupyx import linalg
import gc


from functools import wraps

@array_backend('cupy')
class cupy_backend(ArrayBackendBase):
    """
        https://docs.cupy.dev/en/v9.6.0/reference/index.html

        Although it is possible to generate code logic simultaneously
        compatible with scipy and numpy, implementing it twice lets
        ArrayBackendContext manage memmory more easily
    """
    _arrprefix = cp
    _sciprefix = scp
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

    @keep_reference    
    def chunk_split2d(cls,input,chk_size,axis=-1,discard_padded=False):
        
        in_len = input.shape[axis]
        n_chunks = int(cp.ceil(in_len/chk_size))
        n_spl_to_pad = int(n_chunks*chk_size-in_len)
                
        if discard_padded and n_spl_to_pad:
            n_chunks -= 1
            idx_to_keep = [slice(None)]*input.ndim
            idx_to_keep[axis] = slice(int(n_chunks*chk_size))
            input_padded = input[tuple(idx_to_keep)]        
        elif n_spl_to_pad:
            pad_width = cp.zeros([input.ndim, 2],dtype=int)
            pad_width[axis,:] = [0, n_spl_to_pad] #[before,after] signal
            input_padded = cp.pad(array = input,
                                pad_width = pad_width,
                                constant_values = 0
                                )
        else:
            input_padded = input

        new_shape = cp.asarray(input.shape)
        new_shape[axis] = n_chunks
        new_shape = cp.append(new_shape,chk_size)
        input_chk = input_padded.reshape(new_shape)

        return input_chk

    @keep_reference
    def savgol_coeffs(cls,window_length, polyorder, deriv=0, delta=1.0,**kwargs):
        coeffs = savgol_coeffs(window_length, polyorder, deriv=deriv, delta=delta)
        return cls.to_backend(coeffs)

    @keep_reference
    def conv1d(cls,x,weights,axis=-1,mode='mirror',cval=0.0,**kwargs):
        return ndimage.convolve1d(x,weights,axis=axis,mode=mode,cval=cval)

    @keep_reference
    def fftconv(cls,*args,**kwargs):
        if 'axis' in kwargs:
            kwargs['axes'] = kwargs.pop('axis')
        return fftconvolve(*args,**kwargs)

    @classmethod
    def free_mem(cls,arr:cp.ndarray):
        cls.reflist_remove(arr)
        arr.data.mem.free()
        # Acredito que estou usando uma versão antiga do cupy que
        # tem algum tipo de memory leakage que não sei resolver,
        # tentando ser o mais agressivo o possível...
        del arr 
        cp.get_default_memory_pool().free_all_blocks()  

    @classmethod
    def free_all(cls,):
        cls.reflist_deinit()
        gc.collect()
        # warnings.warn('Se pah isso vai fuder tudo, não sei pq')
        cp.get_default_memory_pool().free_all_blocks()
        cp.fft.config.get_plan_cache().clear()

    def get_free_memory():
        # pool = cp.get_default_memory_pool()
        return cp.cuda.Device().mem_info[0]
        # return pool.total_bytes()
