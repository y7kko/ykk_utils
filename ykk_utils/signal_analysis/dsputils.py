import numpy as np


def dB(input,squared_input=False,ref=1):
    input = np.asarray(input)
    if squared_input:
        mult=10
    else:
        mult=20
    return mult*np.log10(abs(input)/ref)


def norm_max(input,axis=-1):
    input = np.asarray(input)
    return input / abs(input).max(axis=axis,keepdims=True)



def rms(input,axis=-1):
    return np.sqrt(np.mean(abs(input)**2,axis=axis))
