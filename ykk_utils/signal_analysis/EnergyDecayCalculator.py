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
# from ykk_utils.signal_analysis.noisefloor.lundeby_unvectorized import lundeby_unvec
from ykk_utils.signal_analysis.noisefloor.lundeby_unvec import lundeby_unvec

import warnings
"""Todo: 
- Normalizar depois de filtrar...

"""
class EnergyDecayCalculator:
    def __init__(self,ht=None,time=None,fs=None):
        self.ht = ht
        self.time = time
        self.noise_method = None
        self.compensate_noise = False
        self.fs = fs
        if fs is not None:
            self.filterConfig(fs=self.fs,nthoct=3)

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
                  normalize=False,time_trunc=False,headroom=0 ):
        if input is None:
            input = self.ht
        
        print('Filtering')
        output = self._filterSignal(input, band, axis = axis, normalize = normalize)
        if self.noise_method is None:
            output = self._rcumsum(output**2, axis = axis, normalize = False)
        elif self.noise_method =='lundeby':
            print('Lundeby')
            t = dsp.tvec(output.shape[axis],self.fs)
            self.t_cross = self._get_lundeby_tc(output,
                                                headroom=headroom,
                                                axis=axis)
            
            # t_cross, C_comp = self.ndetector.find_crosspoint(ht=output,axis=axis)
            if time_trunc:
                output,t=self._time_trunc(output,
                                 crop_instant=max(self.t_cross),
                                 )
                
            for idx in range(output.shape[0]):
                mint = min(self.t_cross)
                output[idx,:] = self._rcumsum_crop(signal=output[idx,:]**2,
                                                   time_vector=t,
                                                   crop_instant=mint,
                                                   normalize=normalize
                                                   )
        return output

    def _get_lundeby_tc(self,signal,headroom=0,axis=-1,**kwargs):
        t_cross = lundeby_unvec(ht=signal,
                        fs=self.fs,
                        axis=axis,
                        headroom=headroom,
                        on_nonconvergence='mean',**kwargs
                        )
        return t_cross

    def _time_trunc(self,signal,time_vector,crop_instant,axis=-1):
        outslice = [slice(None)]*signal.ndim
        outslice[axis] = slice(int(crop_instant*self.fs))
        signal = signal[tuple(outslice)]
        time_vector = time_vector[outslice[axis]]
        return signal,time_vector

    @property
    def f_nominal(self,):
        return self.filter_obj.f_nominal

    def _rcumsum_crop(self,signal,time_vector,crop_instant,normalize=False):
        tmask = np.where(time_vector < crop_instant)[0]
        signal[tmask] = self._rcumsum(signal[tmask], 
                                            normalize = normalize
                                            )
        signal[(time_vector >= crop_instant) ] = np.finfo(float).eps
        return signal

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
