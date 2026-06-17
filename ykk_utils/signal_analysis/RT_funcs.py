"""Implementa métodos de cálculo relacionados
ao calculo do Tempo de Reverberação
"""
import numpy as np
from typing import overload

def rcumsum(ir:np.ndarray,axis=None,normalize=True):
    if axis is None:
        axis = -1
    output = np.cumsum(np.flip(ir,axis=axis), axis=axis)
    output = np.flip(output, axis=axis) 
    if normalize:
        output/= np.max(abs(output), axis=axis, keepdims=True)
    return output

#Computar o T20,T30, EDT
def tr_fit(in_sig, in_t, Ldecay=20, Lstart = None,init_time=None,dB_input=True):
    """Faz uma regressão linear em uma EDC de entrada

    Args:
        in_sig (ndarray): Sinal de entrada
            - Caso dB_input = True
                Assume que in_sig já esteja em dB
            - Caso dB_input = False
                Aplica 10*log(in_sig)
        in_t (ndarray): Vetor temporal correspondente a in_sig.
        Ldecay (int, optional): Condição de decaimento. Defaults to 20.
            - Caso init_time = None (Default):
                O ajuste de curvas será realizado de Lstart até Lstart-Ldecay
            - Caso init_time != None:
                O ajuste será realizado de 
                in_sig(t=init_time) até in_sig(t) = -Ldecay
        Lstart (float, optional): Nível inicial para cálculo do decaimento. Defaults to None.
            - Por padrão, a análise começa em -5 dB (ISO 3382-2).
            - Especificar init_time implica em ignorar Lstart
        init_time (float, optional): Instante de tempo da chegada do som direto. Defaults to None.
        dB_input (bool, optional): Caso False, será aplicado 10*log10(in_sig). Defaults to True.

    Returns:
        a,b (tuple): Resultados da regressão linear 
            f(t) = a*t + b
    """
    if not dB_input:
        in_sig = 10*np.log10(in_sig**2)
    if init_time is None: #TR
        if Lstart == None:
            Lstart = -5
        end = Lstart - Ldecay

        t_idx = np.where((in_sig<=Lstart) & (in_sig>=end))[0]
    else: #EDT ou algo assim
        t_start_idx = np.where(in_t>=init_time)[0]
        end = - Ldecay
        t_idx = np.where(in_sig >= end)[0]
        t_idx = np.intersect1d(t_start_idx,t_idx)

    a, b = np.polyfit(in_t[t_idx], in_sig[t_idx], 1)
    return a, b

def tr_extrapolate(a,b,L = 60):
    """Dado a reta de decaimento a*t + b, extrapola a curva
    até o nível indicado (por padrão 60 <- T60)

    Args:
        a (float): Coeficiente angular da reta
        b (float): Offset da reta
        L (int, optional): Nível de referência. Por padrão
         o código extrapola a curva até -60dB (como indicado na ISO 3382-2) 
         Defaults to 60.

    Returns:
        float: Instante de tempo em que a reta atinge -L (60dB por padrão).
    """
    return ( (-L) - b) / a
