"""
Classe dedicada a calcular a EDC de um sinal. 
"""
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
"""Todo: 
- Normalizar depois de filtrar...

"""
class EnergyDecayCalculator:
    def __init__(self,ht=None,time=None):
        self.ht = ht
        self.time = time
        self.noise_method = None
        self.compensate_noise = False
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
        self.fs = fs
        self.filter_obj:FilterBank = FilterBank(fs,**kwargs)
        self.filter_obj._generate_sos_matrix()
        return self

    def noisedetectionConfig(self,method=None,compensatenoise=False):
        if isinstance(method,str):
            method = method.lower()

        self.noise_method=method
        self.compensate_noise = compensatenoise


    def integrate(self, input = None, band=None, axis=-1, 
                  normalize=False,time_trunc=False ):
        if input is None:
            input = self.ht
        
        print('Filtering')
        output = self._filterSignal(input, band, axis = axis, normalize = normalize)
        if self.noise_method is None:
            output = self._rcumsum(output**2, axis = axis, normalize = False)
        elif self.noise_method =='lundeby':
            print('Lundeby')
            t = dsp.tvec(output.shape[axis],self.fs)
            t_cross, C_comp = lundeby_unvec(ht=output,
                                            fs=self.fs,
                                            axis=(-1 if axis == None else axis),
                                            on_nonconvergence='mean'
                                            )
            if time_trunc:
                #Truncate to the furthest noise crosspoint
                outslice = [slice(None)]*output.ndim
                outslice[axis] = slice(
                    int(np.max(t_cross)*self.fs)
                    )
                output = output[tuple(outslice)]
                t = t[outslice[axis]]

            for idx in range(output.shape[0]):
                tmask = np.where(t < t_cross[idx])[0]
                output[idx,tmask] = self._rcumsum(output[idx,tmask]**2, 
                                                  normalize = False
                                                  )
                output[idx, (t >= t_cross[idx]) ] = np.finfo(float).eps                
                if self.compensate_noise:
                    output += C_comp[idx]
        return output


    @property
    def f_nominal(self,):
        return self.filter_obj.f_nominal

    def _filterSignal(self,input,band,axis=None,normalize=True,**kwargs):
        output= self.filter_obj.filter(input,axis=axis,band=band,**kwargs)
        # Isso aqui só funciona para o caso unidimensional
        if normalize:
            if axis is None:
                axis = -1
            output /= abs(output).max(axis=axis,keepdims=True)
        return output
    
    def _rcumsum(self,input,**kwargs):
        return TR.rcumsum(input,**kwargs)


EnergyDecayCalculator.filterConfig.__doc__ = FilterBank.__init__.__doc__
