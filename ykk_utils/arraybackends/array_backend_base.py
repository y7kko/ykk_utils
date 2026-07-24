# from typing import Protocol
from collections.abc import Iterable
from abc import ABC, abstractmethod
from functools import wraps

import weakref
import gc

import numpy as np
from scipy.signal import savgol_coeffs
class ArrayBackendBase(ABC):
    """ Provides memory management system and documentation for 
    default functions. 


    """

    _arr_reflist:list = None
    _reflist_enabled:bool = False
    
    # Armazenar namespaces preferidos para lidar com arrays (numpy por exemplo)
    # e funções específicas de computação cientifica(scipy por exemplo)
    _arrprefix = None
    _sciprefix = None

    @classmethod
    def reflist_init(cls):
        """Initializes array references list
        system
        """
        if cls._reflist_enabled:
            return
        else: #redundante mas mais legível
            cls._arr_reflist = []
            cls._reflist_enabled =True

    @classmethod
    def reflist_deinit(cls,):
        """Try to securely deinitialize references list
        system
        """
        if not cls._reflist_enabled:
            return

        if cls._reflist_enabled:
            for ref in cls._arr_reflist:
                arr = ref()
                if arr is None:
                    #weakref already deallocated
                    break
                else:
                    cls.free_mem(arr)

            del(cls._arr_reflist)
            cls._reflist_enabled = False

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
            elif ref() is None:
                cls._arr_reflist.remove(ref)


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
        raise NotImplementedError("Backend lacks a '.to_backend()' method")

    @abstractmethod
    def to_numpy(arr,**kwargs) -> np.ndarray: 
        """Converts backend supported array object into
        numpy array

        Args:
            arr (_type_): Array from backend

        Returns:
            np.ndarray: Numpy array
        """
        raise NotImplementedError("Backend lacks a '.to_numpy()' method")

    @abstractmethod
    def free_mem(arr):
        """Deallocate array from memory, if necessary

        Args:
            arr (_type_): _description_
        """
        # raise NotImplementedError("Backend lacks free_mem method")

    @abstractmethod
    @wraps(savgol_coeffs)
    def savgol_coeffs():
        pass

    @abstractmethod
    def chunk_split2d(input,chk_size,axis=-1,discard_padded=False):
       """Separa sinal unidimensional em blocos de `chk_size` amostras.

        Args:
            input (ndarray): Sinal unidimensional
            chk_size (int): número de blocos por amostra
            axis (int): O eixo do vetor que será separado em blocos. Defaults to -1.
            discard_padded (bool, optional): 
                Caso `len(input)` seja divisivel por `chk_size`, o código
                realizará zero padding na entrada. Caso seja preferível
                descartar as amostras excedentes, utilize `True`. Defaults to False.

        Returns:
            ndarray: Sinal separado em blocos, a saída possuí shape (chk_size,n_chunks)
        """

    @abstractmethod
    def free_all():
        """Tenta desalocar tudo o que pode
        """

    def get_free_memory():
        raise NotImplementedError()
