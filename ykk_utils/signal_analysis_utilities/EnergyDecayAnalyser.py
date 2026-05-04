#%%
import numpy as np
from . import RT_funcs as TR
from .FracFilter import FractionalFilter

"""Todo: 
- Normalizar depois de filtrar...

"""
class EDCAnalyser:
    def __init__(self,ht=None,time=None):
        self.ht = ht
        self.time = time
        pass

    def filterConfig(self,fs,**kwargs):
        self.filter_obj:FractionalFilter = FractionalFilter(fs,**kwargs)
        self.filter_obj.generate_sos_matrix()
        return self

    def EDC(self, band=None, input=None, axis=None):
        if input is None:
            input = self.ht
        # if time is None or input is None:
        #     raise ValueError('Function lacks enough data to compute')
        
        output = self._filterSignal(input, band, axis=axis)
        output = self._rcumsum(output,axis=axis)
        return output

    @property
    def f_nominal(self,):
        return self.filter_obj.f_nominal

    def _filterSignal(self,input,band,**kwargs):
        output= self.filter_obj.filter(input,band=band,**kwargs)
        # Isso aqui só funciona para o caso unidimensional
        print("_filterSignal só está funcionando para o caso unidimensional")
        return output/abs(output).max() 

    def _rcumsum(self,input,**kwargs):
        return TR.rcumsum(input,**kwargs)
