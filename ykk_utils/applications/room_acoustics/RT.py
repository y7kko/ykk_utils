import numpy as np
from . import RT_core
from ykk_utils.arraybackends import cross_slice2d

def T20(edc_dB,time,axis=-1):
    """Calculates T20 of an array of impulse responses.
    This algorithm assumes that the input is in decibels
    and doesn't include steady state energy part of EDC.
    Therefore, it is necessary to normalize each signal
    by its maximum before calling this function.

    Args:
        edc (ndarray): Array of normaliezd energy decay 
        curves in decibels.
        time (ndarray): Time vector
        axis (int, optional): time axis. Defaults to -1.

    Returns:
        ndarray: Array of reverberation times
    """
    return _Tn(edc_dB,time,decayLevel=20,axis=axis)


def T30(edc_dB,time,axis=-1):
    """Calculates T30 of an array of impulse responses.
    This algorithm assumes that the input is in decibels
    and doesn't include steady state energy part of EDC.
    Therefore, it is necessary to normalize each signal
    by its maximum before calling this function.

    Args:
        edc (ndarray): Array of normaliezd energy decay 
        curves in decibels.
        time (ndarray): Time vector
        axis (int, optional): time axis. Defaults to -1.

    Returns:
        ndarray: Array of reverberation times
    """
    return _Tn(edc_dB,time,decayLevel=30,axis=axis)

def _Tn(edc_dB,time,decayLevel,axis=-1,):
    """Performs the reverberation time pipeline in each 
    signal. This local function uses conventions proposed 
    by ISO 3382-1:2009, thus, it's not applicable to determination
    of EDT, for example.
    """
    edc_dB = np.atleast_2d(edc_dB)
    n_meas = edc_dB.shape[not axis]
    TR_arr = np.zeros(n_meas)
    for idx in range(n_meas):
        selector = [slice(None)]*edc_dB.ndim
        selector[not axis] = idx
        a,b = RT_core.tr_fit(edc_dB[tuple(selector)],time,
                             Ldecay=decayLevel,
                             Lstart=-5
                             )
        TR_arr[idx] = RT_core.tr_extrapolate(a,b)
    return TR_arr

