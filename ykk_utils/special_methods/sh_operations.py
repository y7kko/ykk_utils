"""
Funções que calculam grandezas no espectro de esféricos harmônicos
"""
import warnings
import numpy as np
from functools import wraps



def isotropy(Amn,axis=-1):
    """Dado um vetor Amn, calcula a isotropia do négocio

    Baseado no artigo da Nolan lá
    Args:
        Amn (_type_): _description_
        N (_type_, optional): _description_. Defaults to None.

    Returns:
        float: Coeficiente de isotropia do espectro de esféricos harmônicos
    """

    nm_axis = int(not axis)
    i = np.zeros(Amn.shape[axis])

    # num_slice [0,:] considerando shape [(N+1)^2,T]
    num_slice = [slice(None)]*Amn.ndim
    num_slice[nm_axis] = 0 

    num = abs(Amn[tuple(num_slice)])
    den = abs(Amn).sum(axis = nm_axis)
    i = num/den
    return i



@wraps(isotropy)
def isotropy_vectorized(*args,**kwargs):
    warnings.warn('Prefira `isotropy`')
    return isotropy(*args,**kwargs)
