import numpy as np
import scipy
from scipy import signal
# from .dsp_operations import *
from . import dsp_funcs as dsp_module
#Checar quando que muda as versões etc...
if scipy.__version__:
    sosfreqz = signal.sosfreqz
    pass


class BulkFiltering:
    def __init__(self,Hw_mtx,fs,freq):
        self.Hw_mtx = Hw_mtx
        self.fs = fs
        self.freq = freq

    def filter_matrix(self,sos,):
        w,h = sosfreqz(sos,
                       worN=self.freq,
                       whole=False,
                       fs=self.fs
                       )
        self.Hw_mtx *= h.reshape(1,len(h))
        return self.Hw_mtx
    
    def butterworth_design(self,order,fc,kind='low',**kwargs):
        kwargs = {
            **dict(N=order,Wn=fc,fs=self.fs,output='sos',btype=kind),
            **kwargs
            }
        filter = signal.butter(**kwargs)
        return filter
    