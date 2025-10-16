import numpy as np
import os

_oct_center_freqs = None
_oct_minmax_freqs = None
_thrd_center_freqs = None
_thrd_minmax_freqs = None


def _load_file(filename):
    module_dir = os.path.dirname(__file__)
    path= os.path.join(module_dir,'data',filename)
    return np.loadtxt(path,delimiter=',')
    

class OctaveBands:
    @staticmethod
    def center_freqs(): #Faz caching a nivel de modulo
        global _oct_center_freqs
        if _oct_center_freqs is None:
            _oct_center_freqs = _load_file('oct.csv')
        return _oct_center_freqs

    @staticmethod
    def minmax_freqs(): #Faz caching a nivel de modulo
        global _oct_minmax_freqs

        if _oct_minmax_freqs is None:
            _oct_minmax_freqs = _load_file('oct_minmax.csv')
        return _oct_minmax_freqs
    
    @staticmethod
    def get_band(freq=1000):
        center_freqs = OctaveBands.center_freqs()
        minmax_freqs = OctaveBands.minmax_freqs()
        idx = (abs(center_freqs-freq)).argmin()
        return center_freqs[idx], minmax_freqs[idx]



class ThirdOctaveBands:
    @staticmethod
    def center_freqs():
        global _thrd_center_freqs
        if _thrd_center_freqs is None:
            _thrd_center_freqs = _load_file('third_oct.csv')
        return _thrd_center_freqs

    @staticmethod
    def minmax_freqs():
        global _thrd_minmax_freqs
        if _thrd_minmax_freqs is None:
            _thrd_minmax_freqs = _load_file('third_oct_minmax.csv')
        return _thrd_minmax_freqs

    @staticmethod
    def get_band(freq=1000):
        center_freqs = ThirdOctaveBands.center_freqs()
        minmax_freqs = ThirdOctaveBands.minmax_freqs()
        idx = (abs(center_freqs-freq)).argmin()
        return center_freqs[idx], minmax_freqs[idx]
