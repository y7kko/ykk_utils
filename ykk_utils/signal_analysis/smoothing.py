#%%
import numpy as np
from . import RT_funcs as TR
from .FilterBank import FilterBank
from scipy.signal import savgol_filter
from tqdm import tqdm

from ykk_utils.arraybackends import ArrayBackendManager, ArrayBackendContext
from ykk_utils.arraybackends import array_slicetools as arrslice
from ykk_utils.tools.waitbar import tqdm_flush
from ykk_utils.signal_analysis import dsp_funcs as dsp
from ykk_utils.signal_analysis.noisefloor.lundeby_unvectorized import lundeby_unvec

from ykk_utils.arraybackends.array_checker import *


def savgol(signal,winsize,axis=-1,backend='numpy',chunk_size=None):
    """Applies savitzky-golay filtering to an array by means of
    fast convolution.

    Args:
        signal (_type_): _description_
        winsize (_type_): _description_
        axis (int, optional): _description_. Defaults to -1.
        backend (str, optional): _description_. Defaults to 'numpy'.
        chunk_size (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if winsize%2 ==0:
        winsize +=1            

    n_pad = int(winsize/2)
    savgol_kernel = ArrayBackendManager(backend).get_backend().savgol_coeffs(window_length = winsize,
                                                                            polyorder = 2, axis = axis,
                                                                            keep_reference = False
                                                                            )
    # Kernel reshaping
    krn_slice = [np.newaxis]*signal.ndim
    krn_slice[axis] = slice(None)
    savgol_kernel = savgol_kernel[tuple(krn_slice)]

    # Signal padding
    output = np.zeros(signal.shape)
    
    for lims, chunk in arrslice.arr_split2d(signal, chunk_size, axis=axis,waitbar=True):
        idxs = arrslice.cross_slice2d(signal.ndim, lims[0], lims[1],axis= axis)

        #Botar aqui reduz eficiencia, mas evita alocação desnecessaria
        pad_width = np.zeros([chunk.ndim,2],dtype=int)
        pad_width[axis,:] = n_pad
        chk_pad = np.pad(chunk,pad_width=pad_width, mode='reflect')

        with ArrayBackendContext(backend) as yp:
            output_chk = yp.to_backend(chk_pad)
            smoothed_chk = yp.fftconv(output_chk,
                                      savgol_kernel,
                                      mode='same',axis=axis)
            # Remove as partes em que realizei padding
            unpad_slice = [slice(None)]*smoothed_chk.ndim
            unpad_slice[axis] = slice(n_pad,-n_pad)
            smoothed_chk = smoothed_chk[tuple(unpad_slice)]

            #Voltando ao numpy 
            smoothed_chk_np = yp.to_numpy(smoothed_chk)
            output[idxs] = smoothed_chk_np
    yp = ArrayBackendManager(backend).get_backend()
    yp.free_mem(savgol_kernel)
    return output



def _savgol_old(signal,winsize,axis=-1,backend='numpy',chunk_size=None):
    """
        Computes savgol by means of ndimage.convolve1d. As convolve1d uses
        the sliding window method, this function presents slower performance
        when using large arrays. Additionaly, converting results back to numpy
        is unstable in the version I use(Cupy 9.6.0 + CUDA 10.1), I think it is
        related to cupy's internal memory management.

    Args:
        signal (_type_): _description_
        winsize (_type_): _description_
        axis (int, optional): _description_. Defaults to -1.
        backend (str, optional): _description_. Defaults to 'numpy'.
        chunk_size (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if winsize%2 ==0:
        winsize +=1            

    savgol_kernel = ArrayBackendManager(backend).get_backend().savgol_coeffs(window_length = winsize,
                                                                            polyorder = 2, axis = axis,
                                                                            keep_reference = False
                                                                            )
        
    for lims, chunk in arrslice.arr_split2d(signal, chunk_size, axis=axis,waitbar=True):
        idxs = arrslice.cross_slice2d(signal.ndim, lims[0], lims[1],axis= axis)

        with ArrayBackendContext(backend) as yp:
            output_chk = yp.to_backend(chunk)
            smoothed_chk  = yp.conv1d(output_chk, 
                                        savgol_kernel,
                                        axis=axis, 
                                        mode='mirror')
            smoothed_chk_np = yp.to_numpy(smoothed_chk)
            signal[idxs] = smoothed_chk_np
    yp = ArrayBackendManager(backend).get_backend()
    yp.free_mem(savgol_kernel)
    return signal


