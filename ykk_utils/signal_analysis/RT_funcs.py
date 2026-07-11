"""Implementa métodos de cálculo relacionados
ao calculo do Tempo de Reverberação
"""
import numpy as np
from typing import overload

from ykk_utils import dsp_funcs as dsp
from ykk_utils.arraybackends import ArrayBackendManager,ArrayBackendContext
from ykk_utils.arraybackends import array_slicetools as arrslice

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


# modified lundeby method
def modified_lundeby(ht,fs,axis=-1,backend='numpy',chunk_size=None):
    raise NotImplementedError('Ainda não terminei de implementar')

    dB = lambda x: 10*np.log10(x)    
    t = dsp.tvec(len(ht),fs)

    edc_mtx = np.zeros(ht.shape)
    for lims, chunk in arrslice.arr_split2d(ht, chunk_size, axis=axis,waitbar=True):
        idxs = arrslice.cross_slice2d(edc_mtx.ndim, lims[0],lims[1],axis=axis)

        with ArrayBackendContext(backend) as yp:
            ynp = ArrayBackendManager(backend).get_backend()
            chk_size = int(10E-3*fs)
            ht_chk = yp.chunk_split2d(chunk,chk_size=chk_size)
            
            # Falta um método de calcular rms, acreidto que
            # a melhor forma seja na verdade uma forma de obter
            # o namespace de arrays (np,cp), ao invés de sair
            # implementando coisa adoidado
            # ht_chk = 

    # Parei aqui
    # yp.chunk_split2d(ht,chk_size=chk_size,discard_padded=True)
    ht_chk = dsp.chunk_split(ht,chk_size=chk_size,discard_padded=True)
    ht_chk = np.sqrt(np.mean(ht_chk**2,axis=1))
    t_chk = dsp.chunk_split(t,chk_size=chk_size,discard_padded=True)
    t_chk = np.mean(t_chk,axis=1)

    noise_est_len = int(len(t_chk)*.01)
    noise_est = np.sqrt(np.mean(ht_chk[-noise_est_len:]**2))

    reg_idx = np.where(
        dB(ht_chk**2)>=(dB(noise_est**2)+5)
        )[0]

    a, b = np.polyfit(x=t_chk[reg_idx],
                    y=dB(ht_chk[reg_idx]), deg=1)

    chk_size = int((-10/(5*a))*fs) #(5/10) blocks/dB
    ht_chk = dsp.chunk_split(ht,chk_size=chk_size,discard_padded=True)
    ht_chk = np.sqrt(np.mean(ht_chk**2,axis=1))
    t_chk = dsp.chunk_split(t,chk_size=chk_size,discard_padded=True)
    t_chk = np.mean(t_chk,axis=1)

    knee_idx = _knee_maxchord(t_chk,ht_chk)

    # Ajustar uma reta entre t=0 e tn tal que h^2(tn)=noise+10dB.
    # A partir disso, extrapolar após região de truncamento para
    # compensar o truncamento por ruído
    max_reg_idx = np.where(
            dB(ht_chk) >= #h(t)
            dB(np.sum(ht_chk[knee_idx:]**2)) + 10 #noise estimation + 10dB
        )[0][-1]
    a, b = np.polyfit(x=t_chk[:max_reg_idx],
                    y=dB(ht_chk[:max_reg_idx]), deg=1)
    # O valor de truncamento
    Ccomp = np.sum(10**((a*t_chk[knee_idx:]+b)/10))
    
    return t_chk[knee_idx], Ccomp

def _knee_maxchord(x,y,axis=-1):
    """Retorna indíce onde se encontra knee point utilizando 
    implementação (empírica) de TMDSM. O método considera a inflexão 
    como o ponto de maior distância perpendicular à um segmento de 
    reta formado por (x0,y0) e (xn,yn), em que n representa o 
    último par ordenado do meu conjunto de dados.

    A distância entre ponto e reta, então, é determinada por
    formula clássica da geometria analítica [1]. Como os dados são
    normalizados a priori, e a magnitude da distância é irrelevante ao problema, 
    pode-se reduzir a equação
        ```
        d = abs((y[-1]-y[0])*x -(x[-1]-x[0])*y + x[-1]*y[0] -y[-1]*x[0])
        d /= np.sqrt((y[-1] - y[0])**2 + (x[-1] - x[0])**2)
        return d.argmax()
        ```
    por
        ```
        d = abs(x+y).argmin(),
        ```
    Args:
        x (ndarray): Valores de x
        y (ndarray): Valores de y

    Returns:
        int: índice em que se encontra ponto de inflexão geométrico.

    References:
        Ref [1]: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
    """
    np_kw = dict(axis=axis,keepdims=True)
    # Normalizing x and y
    x = (x - np.min(x,**np_kw)) / (np.max(x,**np_kw) - np.min(x,**np_kw))
    y = (y - np.min(y,**np_kw)) / (np.max(y,**np_kw) - np.min(y,**np_kw))    
    return abs(x+y).argmin()
