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


    def integrate(self, input = None, band=None, axis=-1, 
                  smoothing_time=None, normalize=False,
                  backend='numpy',chunk_size=None,noise_detection_method:str='lundeby'):
        if input is None:
            input = self.ht
        
        print('Filtering')
        output = self._filterSignal(input, band, axis = axis, normalize = normalize)
        if noise_detection_method is None:
            output = self._rcumsum(output**2, axis = axis, normalize = False)
        elif noise_detection_method.lower() =='lundeby':
            print('Lundeby')
            t = dsp.tvec(output.shape[axis],self.fs)
            t_cross, C_comp = lundeby_unvec(ht=output,
                                            fs=self.fs,
                                            axis=(-1 if axis == None else axis)
                                            )
            # Truncar a matriz
            print(t_cross.shape)
            print(C_comp.shape)
            max_t_idx = abs(t-t_cross.max()).argmin()
            print(f"Truncando no indice {max_t_idx}: {t[max_t_idx]}")
            t = t[:max_t_idx]
            out_trunc_slice = [slice(None)]*output.ndim
            out_trunc_slice[axis] = slice(0,max_t_idx)
            output = output[tuple(out_trunc_slice)]

            print('EDC')
            #fdc por enquanto vai assim msm
            # for idx in range(3):
            for idx in range(output.shape[0]):
                tmask = np.where(t<t_cross[idx])[0]

                output[idx,tmask] = self._rcumsum(output[idx,tmask]**2, normalize = False)
                output[idx,t >= t_cross[idx]] = 0
            
            output += C_comp

        if smoothing_time is not None:
            print('Smoothing')
            winsize = int(self.fs*smoothing_time)
            if winsize%2 ==0:
                winsize +=1            

            kernel = ArrayBackendManager(backend).savgol_coeffs(window_length = winsize,
                                                                polyorder = 2, axis = saxis,
                                                                keep_reference = False
                                                                )
            
            for lims, chunk in arrslice.arr_split2d(output, chunk_size, axis=axis,waitbar=True):
                idxs = arrslice.cross_slice2d(output.ndim, lims[0], lims[1],axis= axis)

                with ArrayBackendContext(backend) as yp:
                    output_chk = yp.to_backend(chunk)
                    smoothed_chk  = yp.conv1d(output_chk, kernel,axis=axis, mode='mirror')
                    output[idxs] = yp.to_numpy(smoothed_chk)
            ArrayBackendManager(backend).free_mem(kernel)


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


def _savgol_pyfor(input,winlen,axis=-1,**kwargs):
    n_iter = input.shape[0]
    bar = tqdm(total = n_iter, 
            desc = 'Appyling Savgol...')

    for iter in range(n_iter):
        # dynslice = [slice(None)]*input.ndim
        # dynslice[axis] = iter
        input[iter,:] = savgol_filter(input[iter,:],
                                   window_length=winlen,
                                   polyorder=2,
                                #    axis=saxis,
                                   mode='mirror')
        bar.update(1)
    return input # A operação é performada no mesmo lugar
