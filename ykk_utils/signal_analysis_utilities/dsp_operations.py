"""Códigos para operações gerais de processamento de sinais
"""
import numpy as np
import scipy
from scipy import signal


def complete_missing_frequencies(input_freq:np.ndarray,
                                  input_spk:np.ndarray, fs,nonzero=True):
    """Dado um espectro truncado, as extremidades do espectro
    com zero 

    Args:
        input_freq (np.ndarray): O vetor de frequências do seu espectro
        input_spk (np.ndarray): Os coeficientes de cada frequência
        fs (int): Frequência de amostragem
        nonzero (bool): Caso true, adicionar um valor mínimo

    Returns:
        np.ndarray: input_spk com padding [0:fs/2]
    """
    # infering df
    df = input_freq[1]-input_freq[0]
    
    
    nfft = int(fs/df) # tamanho total do vetor que eu quero

    # metade do vetor(até nyquist)
    if (nfft % 2) == 0:
        nfft_half = int(nfft/2)
    else:
        nfft_half = int((nfft+1)/2)
        

    out_spk = np.zeros(nfft_half, dtype = input_spk.dtype)

    # Indíce em que começa e termina o input no novo vetor
    input_init_idx = int(round(input_freq[0]/df)) #rounding prevents numerical instabilities
    input_last_idx = int(round(input_freq[-1]/df))

    # Dumping old spectrum into the new zero padded spectrum
    out_spk[input_init_idx:input_last_idx+1] = input_spk

    #Quase zero
    out_spk[np.where(out_spk==0)[0]] = np.finfo(out_spk.dtype).tiny


    return out_spk


def generate_frequency_vector(fs,nfft=None,df=None,input_freq=None,half_spectrum=True):
    """
    Gera um vetor de frequências baseado na taxa de amostragem e resolução de frequência.
    
    A função cria um vetor de frequências linearmente espaçado de 0 até fs (ou fs/2),
    dependendo do parâmetro half_spectrum. A resolução de frequência (df) pode ser
    fornecida diretamente ou inferida a partir de um vetor de frequências de entrada.
    
    Args:
        fs (int or float): Frequência de amostragem em Hz.
        df (float, optional): Resolução de frequência (diferença entre pontos consecutivos).
            Deve ser fornecido se input_freq for None. Default: None.
        input_freq (np.ndarray, optional): Vetor de frequências parcial usado para
            inferir df. Deve ser fornecido se df for None. Default: None.
        half_spectrum (bool, optional): Se True, retorna apenas o espectro de 0 até fs/2.
            Se False, retorna o espectro completo de 0 até fs. Default: True.
    
    Returns:
        np.ndarray: Vetor de frequências linearmente espaçado.
    """
    if nfft is None:
        if df is None:
            # Try to infer df
            try:
                df = input_freq[1]-input_freq[0]
            except:
                raise ValueError("Apenas um dos parâmetros (df ou input_freq) deve ser fornecido")
        nfft = int(fs/df) # tamanho total do vetor que eu quero 

    out_freq = np.linspace(0, (nfft-1)*fs/nfft, nfft)

    # Caso eu queira f = [0 : nyquist]
    if half_spectrum:
        if (nfft % 2) == 0:
            nfft_half = int(nfft/2)
        else:
            nfft_half = int((nfft+1)/2)

        out_freq = out_freq[:nfft_half]
    
    return out_freq

def generate_time_vector(data,fs):
    n_spl = len(data)
    max_time = n_spl/fs
    time_vector = np.arange(0,max_time,1/fs)
    return time_vector
