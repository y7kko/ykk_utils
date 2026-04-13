"""
Funções que calculam grandezas no espectro de esféricos harmônicos
"""
import numpy as np


def isotropy(Amn,N=None):
    """Dado um vetor Amn, calcula a isotropia do négocio

    Baseado no artigo da Nolan lá
    Args:
        Amn (_type_): _description_
        N (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if N is None:
        N = np.sqrt(len(Amn)) - 1

    Amn_sum = np.zeros(N+1)
    for n in range(0,N+1):
        for m in range(-n,n+1):
            # print(f"deg {n} ordr {m}")
            # print(counter)

            Amn_sum[n] += np.abs(Amn[counter])
            # print(f"idx {counter} \t- A{n},{m}\t-> {n}")
            counter+=1
    return Amn_sum[0]/np.sum(Amn_sum)
