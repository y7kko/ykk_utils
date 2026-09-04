import numpy as np
from tqdm import tqdm
from ykk_utils.tools.waitbar import tqdm_flush
from ykk_utils.arraybackends.array_slicetools import arr_split2d,cross_slice2d
from ykk_utils.arraybackends import ArrayBackendContext,ArrayBackendManager


def get_kernel(coord,k0,directions,normal=None,keepdims=True):
    if normal is None:
        Kernel = H_kernel(coord,k0,directions)
    else:
        axis = _parse_normal_arg(normal)
        Kernel = dHdn_kernel(coord,k0,directions,axis)

    if keepdims:
        return Kernel
    else:
        return Kernel.squeeze()


def H_kernel(coord,k0,directions,) -> np.ndarray:
    """Computes plane wave expansion Kernel for 
    pressure reconstruction.

    Args:
        coord (_type_): _description_
        k0 (_type_): _description_
        directions (_type_): _description_

    Returns:
        _type_: _description_
    """
    k_p = k0[...,np.newaxis,np.newaxis]*directions
    exp_arg = np.einsum('ij,lkj->lik',-1j*coord,k_p) #(M,3) * k (3,n) ->k M,N
    H = np.exp(exp_arg) # k M,N
    return H

def dHdn_kernel(coord,k0,directions,axis) -> np.ndarray:
    """Computes plane wave expansion Kernel 
    derivative with respect of axis

    Args:
        coord (_type_): _description_
        k0 (_type_): _description_
        directions (_type_): _description_
        axis (_type_): _description_

    Returns:
        _type_: _description_
    """
    k_p = k0[...,np.newaxis]*directions[:,axis]
    exp_arg = np.einsum('ij,lkj->lik',-1j*coord[:,axis],k_p) #(M,1) * k (1,n) ->k M,N
    H = np.exp(exp_arg) # k M,N
    return H

def _parse_normal_arg(normal_arg) -> int:
    """Converts normal argument into expected axis convention

    Examples:
        'x' returns 0
        'z' returns 2
        'xy' returns 2 ('z')
        'xz' returns 1 ('y')
    """
    normal_arg:str = str(normal_arg)
    normal_arg = (normal_arg
                  .replace('x','0')
                  .replace('y','1')
                  .replace('z','2')
                  )

    if len(normal_arg) == 1: #input is the desired axis
        return int(normal_arg)
    elif len(normal_arg) == 2: #input is the plane i want to compute the normal
        normal_arg = [idx for idx in list('012') if (not idx in normal_arg)]
        return int(tuple(normal_arg))    
    else:
        raise ValueError('Bad arguments in _parse_normal_arg()')
