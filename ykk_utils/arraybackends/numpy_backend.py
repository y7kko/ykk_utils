from .array_backend_core import array_backend
from .array_backend_base import ArrayBackendBase
import numpy as np
from functools import wraps
from scipy.signal import savgol_coeffs
import scipy.ndimage as ndimage

@array_backend('numpy')
class numpy_backend(ArrayBackendBase):
    @wraps(np.asarray)
    @classmethod
    def to_backend(cls,arr,**kwargs):
        kwargs.pop('keep_reference',None)
        arr_out = np.asarray(arr,**kwargs)
        # cls.reflist_add(arr_out)
        return arr_out

    @wraps(np.asarray)
    def to_numpy(arr,**kwargs):
        return np.asarray(arr,**kwargs)
    
    @wraps(np.fft.rfft)
    def rfft(*args,**kwargs):
        return np.fft.rfft(*args,**kwargs)

    @wraps(np.fft.irfft)
    def irfft(*args,**kwargs):
        return np.fft.irfft(*args,**kwargs)
    
    def norm_max(input,axis=-1):
        return input / abs(input).max(axis=axis,keepdims=True)
    
    def lstsq(*args,**kwargs):
        return np.linalg.lstsq(*args,**kwargs)

    def free_mem(arr:np.ndarray):
        #I think python memory management already handles it well
        pass

    @classmethod
    def savgol_coeffs(cls,window_length, polyorder, deriv=0, delta=1.0,**kwargs):
        coeffs = savgol_coeffs(window_length, polyorder, deriv=deriv, delta=delta)
        return cls.to_backend(coeffs)
    
    @wraps(ndimage.convolve1d)
    def conv1d(x,weights,axis=-1,mode='mirror',cval=0.0,**kwargs):
        return ndimage.convolve1d(x,weights,axis=axis,mode=mode,cval=cval)

    @classmethod
    def __getattr__(cls, key):
        """PS:CHATGPTADO"""
        # Evita recursão infinita
        if key.startswith('__') and key.endswith('__'):
            raise AttributeError(f"'{cls.__name__}' has no attribute '{key}'")
        
        attr = getattr(np, key)
        
        # Opcional: Wrapper para preservar docstring
        if callable(attr):
            @wraps(attr)
            def wrapper(*args, **kwargs):
                return attr(*args, **kwargs)
            return wrapper
        
        return attr
    

    @classmethod
    def __dir__(cls):
        """Melhora a introspecção e autocomplete
        
        PS: CHATGPTADO
        """
        # Combina atributos da própria classe com os do numpy
        own_attrs = set(dir(type(cls))) | set(cls.__dict__.keys())
        np_attrs = set(dir(np))
        return sorted(own_attrs | np_attrs)
