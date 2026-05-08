#%%
import numpy as np
from . import RT_funcs as TR
from .FilterBank import FilterBank

"""Todo: 
- Normalizar depois de filtrar...

"""
class EDCAnalyser:
    def __init__(self,ht=None,time=None):
        self.ht = ht
        self.time = time
        pass

    def filterConfig(self,fs,**kwargs):
        """
        Configure and initialize the fractional filter.
        
        Parameters
        ----------
        fs : float
            Sampling frequency in Hz
        **kwargs : 
            Additional keyword arguments passed directly to 
            `FractionalFilter(fs, **kwargs)` constructor.
            
            For complete parameter documentation, see the 
            `FractionalFilter.__init__` method.
        
        Returns
        -------
        self
            Returns self for method chaining
        """
        self.filter_obj:FilterBank = FilterBank(fs,**kwargs)
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

    def _filterSignal(self,input,band,axis=None,**kwargs):
        output= self.filter_obj.filter(input,axis=axis,band=band,**kwargs)
        # Isso aqui só funciona para o caso unidimensional
        if axis is None:
            output /= abs(output).max()
        else:
            print("_filterSignal não testado para axis != None")
            for idx in range(input.shape[axis]):
                arr_slice = [slice(None)]*input.ndim 
                arr_slice[axis] = idx
                output[tuple(arr_slice)] /= abs(output[tuple(arr_slice)]).max()
        return output
    
    def _rcumsum(self,input,**kwargs):
        return TR.rcumsum(input,**kwargs)
    
EDCAnalyser.filterConfig.__doc__ = FilterBank.__init__.__doc__
