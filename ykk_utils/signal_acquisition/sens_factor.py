import numpy as np
import scipy.signal as scsig

def sens_factor(ref_signal,fs,f_ref=1000,target_rms=1):
    """ Returns a transducer signal sensitivity correction factor
    for periodic signals. This function uses the autospectrum method,
    this means that: for a signal with unity V, its autospectrum Sxx
    has unity V**2, and its correction factor is given by:
    ```
        sens = target_rms(f)/sqrt(Sxx(f)),
    ```
    where f is the `f_ref` reference frequency, in the same units
    as `fs`. Then, a signal y with adjusted amplitude is given by:
    ```
        y_adj = y * sens
    ```

    Args:
        ref_signal (ndarray): Reference signal
        fs (int): Sampling rate
        f_ref (int, optional): Reference frequency. Defaults to 1000.
        target_rms (int, optional): Target rms value after sensitivity adjustment. 
        Defaults to 1.

    Returns:
        float: sensitivity factor to be multiplied
    """
    #Sxx é o autoespectro de signal (unidade_rms^2)
    f,Sxx = scsig.csd(ref_signal,ref_signal,fs,
                      window='hann',nperseg=int(fs/10),
                      scaling='spectrum')
    fidx = (abs(f-f_ref)).argmin()
    y_rms = np.sqrt(abs(Sxx[fidx]))
    return target_rms/y_rms

def apply_sens_factor(arr,sens):
    return arr*sens
