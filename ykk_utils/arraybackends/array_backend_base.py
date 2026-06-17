# from typing import Protocol
from collections.abc import Iterable
from abc import ABC, abstractmethod
import numpy as np
import weakref
import gc

class ArrayBackendBase(ABC):
    _arr_reflist = None
    _reflist_enabled = False
    
    @classmethod
    def reflist_init(cls):
        """Initializes array references list
        system
        """
        if cls._reflist_enabled:
            return
        cls._arr_reflist = []
        cls._reflist_enabled =True

    @classmethod
    def reflist_deinit(cls,):
        """Try to securely deinitialize references list
        system
        """
        if not cls._reflist_enabled:
            return

        cls._reflist_enabled = False
        if cls._reflist_enabled == 0:
            for ref in cls._arr_reflist:
                arr = ref()
                if arr is None:
                    #weakref already deallocated
                    break
                else:
                    cls.free_mem(arr)
            del(cls._arr_reflist)

    @classmethod
    def reflist_add(cls,arr):
        """Append new objects to reflist. This code also supports
        multiple objects in a single iterable
        reflist_add([obj1,obj2,obj3])

        Args:
            arr (ndarray): _description_
        """
        if not cls._reflist_enabled:
            return
        if isinstance(arr,(tuple,list)):
            for arrbit in arr:
                    cls._arr_reflist.append(weakref.ref(arrbit))
            return
        else:   
            cls._arr_reflist.append(weakref.ref(arr))

    @classmethod
    def reflist_remove(cls,arr):
        if not cls._reflist_enabled:
            return

        for ref in cls._arr_reflist[:]:
            if ref() is arr:
                cls._arr_reflist.remove(ref)
                break

    @abstractmethod
    def to_backend(arr:np.ndarray,keep_reference=True,**kwargs):
        """Converts numpy array into a backend supported
        array object

        Args:
            arr (np.ndarray): The array to be converted
            keep_reference (bool): If True, ArrayBackendContext will
                automatically handle memory deallocation of `arr`. If
                false, it will be necessary to call yp.free_mem(arr).
                Defaults to True
        """
        pass

    @abstractmethod
    def to_numpy(arr,**kwargs) -> np.ndarray: 
        """Converts backend supported array object into
        numpy array

        Args:
            arr (_type_): Array from backend

        Returns:
            np.ndarray: Numpy array
        """
        pass

    @abstractmethod
    def free_mem(arr):
        """Deallocate array from memory, if necessary

        Args:
            arr (_type_): _description_
        """
        pass
