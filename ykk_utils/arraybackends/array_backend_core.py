#%%
import warnings
from functools import wraps
import numpy as np
from .array_backend_base import ArrayBackendBase
from ._backend_collection import backend_collection

# _backend_collection = {}
# _backend_attrs = {}


def array_backend(name:str=None):
    """array backend declaration operator. 
    Declares class in backend collection, to be called from
    ArrayBackendManager

    Usage:
        from ykk_utils import ArrayBackendManager

        @array_backend
        class foo():
            def __init__():
                print('bar')

            def a():
                print('a')

        ArrayBackendManager('foo').a()
    """
    print(f'called {name} 2')
    def decorate(cls):
        key = name if name else cls.__name__
        print(key)
        backend_collection[key] = cls
        # _backend_attrs[key] = list(prop for prop in dir(cls) if not prop.startswith('__'))
        return cls
    
    return decorate


def keep_reference(func):
    """Adiciona automaticamente o sistema de gerenciamento de referências,
    usado com ArrayBackendContext para gerenciar memória

    Args:
        func (_type_): _description_

    Returns:
        _type_: _description_
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        keep_ref = kwargs.pop('keep_reference',True)
        result = func(*args, **kwargs)
        if keep_ref:
            # args[0] é 'cls' em classmethods
            if args and hasattr(args[0], 'reflist_add'):
                args[0].reflist_add(result)
        return result
    return classmethod(wrapper)



class ArrayBackendManager():
    def __init__(self,backend_key:str=None, fallback_key:str='numpy'):
        self.backend_key = backend_key
        self.fallback_key = fallback_key

    def get_backend(self,key=None) -> ArrayBackendBase:
        if key:
            return backend_collection[key]
        elif self.backend_key is not None:
            return backend_collection[self.backend_key]
        else:
            warnings.warn(f"Backend not found, using '{self.fallback_key}' instead.")
            return backend_collection[self.fallback_key]
    
    def __str__(self):
        return str(list(backend_collection.keys()))

    def __getattr__(self, attr):
        if hasattr(backend_collection[self.backend_key], attr):
            key = self.backend_key
        elif hasattr(backend_collection[self.fallback_key], attr):
            key = self.fallback_key
            warnings.warn(f"'{attr}' does not exist in '{self.backend_key}' backend, using '{key}' instead")
        else:
            raise AttributeError(f"'{attr}' does not exist in '{self.backend_key}' nor '{self.fallback_key}' backends")
        
        backend_object:ArrayBackendBase = self.get_backend(key)
        method = getattr(backend_object, attr)
        
        #tentando manter metadados do método
        @wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        
        return wrapper
    
    def __repr__(self):
        keys = list(backend_collection.keys())
        output = ''
        output=output+('''::: ArrayBackendManager
              List o available backends:\n
              ''')
        for key in keys:
            output +=print(f'  - {key}\n')
        return output
