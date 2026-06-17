"""Códigos para operações gerais de processamento de sinais
"""
import numpy as np
import scipy
from scipy import signal
from tqdm import tqdm
from ykk_utils.tools.waitbar import tqdm_flush
from ykk_utils.arraybackends import ArrayBackendManager,ArrayBackendContext
from ykk_utils.arraybackends import array_slicetools as arrslice

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

    #Impede zero absoluto (útil para quando dB)
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
    """Gera um vetor de frequências para um dado no tempo

    Args:
        data (ndarray or int): 
            - Caso seja um escalar, é gerado um vetor
              com len(time_vector) = data.
            - Caso seja um vetor, é gerado um vetor com
                len(time_vector) = len(data)
        fs (float): Frequência de amostragem do sinal

    Returns:
        ndarray: Um vetor temporal correspondente aos dados de entrada
    """
    # print('att')
    if np.isscalar(data):
        n_spl = data
    else:
        n_spl = len(data)
    max_time = (n_spl - 1)/fs
    time_vector = np.linspace(0,max_time,n_spl)
    return time_vector


def ifft_trunc(input_spk,freq,fs,normalize=False,axis=-1,backend='numpy',chunk_size=None):
    """Realiza a ifft de um espectro truncado.
    À parte não definida pelo sinal de entrada, são atribuidos zeros.


    Args:
        input_spk (ndarray): Espectro truncado
        freq (ndarray): Frequências do espectro truncado len(freq)==len(input_spk)
        fs (int): Taxa de amostragem
        axis (int): A dimensão em que o código deve operar
            Obs: No momento o axis está hardcoded e assume que a entrada 
            possui shape (dir, freq) ou (freq,)
    Returns:
        _type_: O sinal no tempo
    """
    input_is_unidimensional = False
    if input_spk.ndim == 1:
        input_is_unidimensional = True
    

    if input_is_unidimensional:
        spk_full = complete_missing_frequencies(input_freq = freq,
                                                input_spk = input_spk,
                                                fs = fs
                                                )
    else:
        full_freq = generate_frequency_vector(fs=fs,input_freq=freq,half_spectrum=True)
        spk_full = np.zeros([input_spk.shape[0], len(full_freq)],dtype=complex)
        print('::: Spk Pad')
        for ir_idx in range(input_spk.shape[0]):
            current_spk = input_spk[ir_idx, :]
            spk_full[ir_idx,:] = complete_missing_frequencies(input_freq = freq,
                                                input_spk = current_spk,
                                                fs = fs
                                                )
    out_shape = list(spk_full.shape)
    out_shape[axis] = 2*(out_shape[axis]-1) 
    out_t = np.zeros(out_shape)

    tqdm_flush()
    bar = tqdm(total=out_t.shape[int(not axis)])
    for lims, chunk in arrslice.arr_split2d(spk_full, chunk_size, axis=axis):
        idxs = arrslice.cross_slice2d(out_t.ndim, lims[0],lims[1],axis=axis)

        with ArrayBackendContext(backend) as yp:
            spk_part = yp.to_backend(chunk)     
            chk_ifft = yp.irfft(spk_part, axis=axis) 
            out_t[idxs] = yp.to_numpy(chk_ifft) # casts backend type into ndarray
        bar.update(chunk_size)
    
    if normalize:
        out_t = ArrayBackendManager('numpy').norm_max(out_t,axis=axis) 
    
    return out_t


def time_roll(input_t,fs,t_shift,axis=None):
    """Faz um shift circular no array

    troll e time_roll são equivalentes

    Args:
        input_t (ndarray): o dado(no tempo) que você quer fazer o shift temporal
        fs (int): Frequencia de amostragem
        time (float): o shift temporal (em segundos) que você quer dar
        axis (int, optional): Qual eixo do vetor o shift deve ser feito. Defaults to None.

    Returns:
        ndarray: O sinal com shift circular
    """
    return np.roll(input_t, int(t_shift*fs),axis=axis)


def frequency_roll(input_f,fs,freq,t_shift):
    """Faz um shift circular no tempo de um array na frequência.
    O shift circular é realizado por meio da propriedade do atraso
    da transformada de Fourier, em que
    fft{x(t-t0)} = e^{-j*w*t0} X(jw)

    Note que:
        A função não assume shape da matriz, matrizes com dimensões
        de tamanho igual ao vetor de frequência podem gerar comportamento
        não definido.
    
    
    frequency_troll e ftroll são equivalentes.

    Args:
        input_f (_type_): Sinal de entrada no espectro da frequência
        fs (_type_): Frequência de amostragem
        freq (_type_): Vetor de frequências
        t_shift (_type_): o quanto de shift temporal quero dar 

    Returns:
        _type_: A matriz input_f, multiplicada por uma exponencial
            equivalente a um atraso temporal.
    """
    n_shift = t_shift*fs
    return input_f * np.exp(-1j*np.pi*2*freq*n_shift/fs)


def chunk_split(input,chk_size,discard_padded=False):
    """Separa sinal unidimensional em blocos de `chk_size` amostras.

    Args:
        input (ndarray): Sinal unidimensional
        chk_size (int): número de blocos por amostra
        discard_padded (bool, optional): 
            Caso `len(input)` seja divisivel por `chk_size`, o código
            realizará zero padding na entrada. Caso seja preferível
            descartar as amostras excedentes, utilize `True`. Defaults to False.

    Returns:
        ndarray: Sinal separado em blocos, a saída possuí shape (chk_size,n_chunks)
    """
    in_size = len(input)
    n_chunks = int(np.ceil(in_size/chk_size))

    n_pad = int(n_chunks*chk_size-in_size)
    input_padded = np.pad(array=input,pad_width=(0,n_pad),constant_values=0)
    input_padded = input_padded.reshape(n_chunks,chk_size)
    if discard_padded and n_pad:
        return input_padded[:-1,:]
    else:
        return input_padded


#Aliases
troll = time_roll
ftroll = frequency_roll

tvec = generate_time_vector
fvec = generate_frequency_vector
