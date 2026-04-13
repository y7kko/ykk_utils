import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import pytta
from typing import overload, Union


@overload
def spectrogram(time_signal: np.ndarray, fs: float, /,
                signal_kw: dict = {}, plot_kw: dict = {}, cbar_kw: dict = {}): ...
@overload
def spectrogram(time_signal: pytta.SignalObj, /,
                signal_kw: dict = {}, plot_kw: dict = {}, cbar_kw: dict = {}): ...



def spectrogram(time_signal: Union[np.ndarray, pytta.SignalObj], 
                fs: float = None, /,
                signal_kw: dict = {}, plot_kw: dict = {}, cbar_kw: dict = {}):
    """
    Plota espectrograma de um sinal.
    
    Parâmetros:
    -----------
    time_signal : np.ndarray ou pytta.SignalObj
        Sinal no tempo
    fs : float, opcional
        Frequência de amostragem (obrigatório se time_signal for np.ndarray)
    signal_kw : dict
        Parâmetros para signal.spectrogram
    plot_kw : dict
        Parâmetros para plt.pcolormesh
    cbar_kw : dict
        Parâmetros para plt.colorbar
    return_objects : bool
        Se True, retorna dicionário com objetos matplotlib
    """
    
    # Extrair dados dependendo do tipo de entrada
    if isinstance(time_signal, pytta.SignalObj):
        fs = time_signal.samplingRate
        time_signal_array = time_signal.timeSignal.T[0]
        # print(f"Usando pytta.SignalObj com fs={fs} Hz")
    elif isinstance(time_signal, np.ndarray):
        time_signal_array = time_signal
        if fs is None:
            raise ValueError("Parâmetro 'fs' é obrigatório quando time_signal é np.ndarray")
        # print(f"Usando np.ndarray com fs={fs} Hz")
    else:
        raise TypeError(f"time_signal deve ser np.ndarray ou pytta.SignalObj, recebeu {type(time_signal)}")
    
    signal_kw = {**{'nperseg': 512, 'noverlap': 256, 
                    'window': 'hann', 'scaling': 'spectrum'},
                 **signal_kw}
    
    f, t, Sxx = signal.spectrogram(time_signal_array, fs, **signal_kw)
    
    if plt.get_fignums():
        plt.gcf()
    else:
        plt.figure(figsize=(9, 3))

    plot_kw = {**{'shading': 'gouraud', 'vmin': -60, 'cmap': 'inferno'},
               **plot_kw}
    
    Sxx_dB = 10 * np.log10(Sxx / np.amax(Sxx) + 1E-10)
    p = plt.pcolormesh(t, f, Sxx_dB, **plot_kw)
    
    cbar_kw = {**{'label': 'Magnitude (dB)'}, **cbar_kw}
    cbar = plt.colorbar(p, **cbar_kw)
    
    # Configurar labels
    plt.ylabel('Frequency (Hz)')
    plt.xlabel('Time (s)')
