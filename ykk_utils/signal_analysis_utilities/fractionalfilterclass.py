# -*- coding: utf-8 -*-

import numpy as np
from copy import copy
from scipy import signal as ss
from pytta.classes import SignalObj
from pytta.classes._base import ChannelsList
from pytta.utils import fractional_octave_frequencies, freq_to_band, \
                        normalize_frequencies, freqs_to_center_and_edges
from tqdm import tqdm
import os
from.FractionalBands import OctaveBands, ThirdOctaveBands

class FractionalFilterBase(object):
    """Base class for filters."""

    def __init__(self, order: int, samplingrate: int):
        self.samplingRate = samplingrate
        self.order = order
        return

    def __call__(self, sigobj: SignalObj):
        """
        Filter the signal object.

        For each channel inside the input signalObj, will be generated a new SignalObj with the channel filtered signal.

        Args:
            sigobj: SignalObj

        Return:
            output: List
                A list containing one SignalObj with the filtered data for each channel in the original signalObj.

        """
        return self.filter(sigobj)



class OctFilter(FractionalFilterBase):
    """
    (DEPRECATED) Octave filter. This class is being kept for retrocompatibility purposes. 
    It is an adaptation of PyTTa filtering classes to work with InsituMeasurementPostPro ht_mtx arrays.
    """
    def __init__(self,
                 order: int = None,
                 nthOct: int = None,
                 samplingRate: int = None,
                 minFreq: float = None,
                 maxFreq: float = None,
                 refFreq: float = None,
                 base: int = None) -> None:
        """

        Parameters
        ----------
        order : int, optional
            Ordem do filtro. The default is None.
        nthOct : int, optional
            Numero de Frações de oitava. The default is None.
        samplingRate : int, optional
            Taxa de amostragem. The default is None.
        minFreq : float, optional
            Menor frequência central(intervalo fechado). The default is None.
        maxFreq : float, optional
            Maior frequência central(intervalo fechado). The default is None.
        refFreq : float, optional
            Frequência de referência. The default is None.
        base : int, optional
            Base do logaritmo, n sei pq eu mudaria isso. The default is None.

        Returns
        -------
        None
            DESCRIPTION.

        """
        FractionalFilterBase.__init__(self, order, samplingRate)
        self.nthOct = nthOct
        self.minFreq = minFreq
        self.minBand = freq_to_band(minFreq, nthOct, refFreq, base)
        self.maxFreq = maxFreq
        self.maxBand = freq_to_band(maxFreq, nthOct, refFreq, base)
        self.refFreq = refFreq
        self.base = base
        self.sos = self.get_sos_filters()
        return

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        if traceback is None:
            return
        else:
            raise value

    def __design_sos_butter(self,
                            bandEdges: np.ndarray,
                            order: int = 4,
                            samplingRate: int = 44100) -> np.ndarray:
        sos = np.zeros((order, 6, len(bandEdges)))
        for i, edges in enumerate(bandEdges):
            if edges[1] >= samplingRate//2:
                edges[1] = samplingRate//2 - 1
            sos[:, :, i] = ss.butter(N=order, Wn=np.array([edges[0],
                                                          edges[1]]),
                                     btype='bp', output='sos', fs=samplingRate)
        return sos

    def get_sos_filters(self) -> np.ndarray:
        freqs = fractional_octave_frequencies(self.nthOct,
                                              (self.minFreq,
                                               self.maxFreq),
                                              self.refFreq,
                                              self.base)
        self.center, edges = freqs_to_center_and_edges(freqs)
        return self.__design_sos_butter(edges, self.order, self.samplingRate)

    # def filter(self, sigobj):
    #     print(":WARNING: `OctFilter.filter` method will soon be deprecated.")
    #     return self._filter(sigobj)
    
    def filter_mtx(self, ht_mtx,band_indexes=None):
        """
        Filter the signal object.

        For each channel inside the input signalObj, will be generated a new
        SignalObj with the channel filtered signal.

        Args:
            sigobj: SignalObj

        Return:
            output: List
                A list containing one SignalObj with the filtered data for each
                channel in the original signalObj.

        """
        if band_indexes is None:
            n = self.sos.shape[2]
            band_indexes = np.arange(0,n)
        else:
            n = len(band_indexes)

    
        out_mtx = np.zeros(np.append(ht_mtx.shape,[n])) #[jrec,time,n]
        
        
        progress_bar = tqdm(total=out_mtx.shape[0]*n)
        for rec_idx in range(out_mtx.shape[0]):
            for band_idx in range(n):
                filtered = ss.sosfilt(self.sos[:, :, band_indexes[band_idx]].copy(order='C'),
                                                            ht_mtx[rec_idx,:], #.copy(order='C')
                                                            axis=0).T
           
                out_mtx[rec_idx, :, band_idx] = filtered
                progress_bar.update(1)

        return out_mtx
    

    def filter_mtx_cached(self,file, ht_mtx,band_indexes=None,):
        """
        Filter the signal object.

        For each channel inside the input signalObj, will be generated a new
        SignalObj with the channel filtered signal.

        Args:
            sigobj: SignalObj

        Return:
            output: List
                A list containing one SignalObj with the filtered data for each
                channel in the original signalObj.

        """
        if band_indexes is None:
            n = self.sos.shape[2]
            band_indexes = np.arange(0,n)
        else:
            n = len(band_indexes)

        n_irs = ht_mtx.shape[0]
        n_t = ht_mtx.shape[1]
        #out_mtx = np.zeros(np.append(ht_mtx.shape,[n])) #[jrec,time,n]
        out_mtx = np.memmap(file, dtype=np.float64, mode='w+', 
                                  shape=(n_irs, n_t, n))
        
        progress_bar = tqdm(total=out_mtx.shape[0]*n)
        for rec_idx in range(out_mtx.shape[0]):
            for band_idx in range(n):
                filtered = ss.sosfilt(self.sos[:, :, band_indexes[band_idx]].copy(order='C'),
                                                            ht_mtx[rec_idx,:], #.copy(order='C')
                                                            axis=0).T
           
                out_mtx[rec_idx, :, band_idx] = filtered
                progress_bar.update(1)

        return out_mtx
    
    def get_band_freqs(self,rounding=0) -> 'float':
        module_dir = os.path.dirname(__file__)

        if self.nthOct == 1:            
            bandlist = OctaveBands.center_freqs()
        elif self.nthOct == 3:
            bandlist = ThirdOctaveBands.center_freqs()
        else: #early return
            idx_min = self.nthOct*np.log2(self.minFreq/self.refFreq)
            idx_max = self.nthOct*np.log2(self.maxFreq/self.refFreq)
            idx = np.arange(idx_min,idx_max+1,1)
            bandlist = np.round(self.refFreq * 2**(idx/(self.nthOct)),rounding)
            return bandlist
        
        idx = np.where((bandlist>=self.minFreq) & (bandlist <= self.maxFreq))
        return bandlist[idx]


    @property
    def filter(self,**kwargs): 
        return self.filter_mtx(**kwargs)
