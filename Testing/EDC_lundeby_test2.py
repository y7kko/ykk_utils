#%%
import numpy as np
import matplotlib.pyplot as plt

from ykk_utils.file_management.colab_tools import colabrw as rwops
from ykk_utils.signal_analysis import dsp_funcs as dsp
from ykk_utils.special_methods.SHMatrix import SHMatrixProcessor
from ykk_utils import EnergyDecayCalculator
from ykk_utils.tools.SmallScripts import audio
# from tessellation import SphereTessellator
from ykk_utils import ThirdOctaveBands,ykplot,GlobalWorkspace as glws
from ykk_utils import dsputils
from ykk_utils.applications import DirectionalDecay
import os
from ykk_utils.special_methods import sh_operations as shops
from ykk_utils.signal_analysis.smoothing import savgol
def flimit(spk,freq,flims):
    fidx = np.where((freq>=flims[0]) & (freq<=flims[1]))[0]
    return spk[:,fidx],freq[fidx]

def half_time(ir,mult=(1/2)):
    end = int(ir.shape[1]*mult)
    return ir[:,:end]

def yellow(string):
    return  "\033[33m" + string + "\033[0m"

def dictreader(path,flims=[0,44100/2]):
    datadict = rwops.read_hdf5(filename=path)
    datadict['pk'],datadict['freq'] = flimit(datadict['pk'],datadict['freq'],flims)
    return datadict

#%% Extraindo os dados do .hdf5
flims = [80,2.5E3]
_datadicts = {}
def register_dict(label,datadict):
    global _datadicts
    label=label.lower()
    _datadicts[label] = datadict

# path =r"D:\Documents\UFSM\Pesquisa - Eric\Cloud\Processed\s2_nearfloor\empty_Lcm_dcm_300pt_12072026_decomposition_36s_crop.hdf5"
# datadict = dictreader(path,flims)
# register_dict('empty',datadict)

path =r"D:\Documents\UFSM\Pesquisa - Eric\Cloud\Processed\s2_nearfloor\PET_L5cm_300pt_04082026_decomposition_36s_crop.hdf5"
datadict = dictreader(path,flims)
register_dict('pet',datadict)

fs = 44100
EDCalc = EnergyDecayCalculator().filterConfig(fs,nthoct=3)

EDCalc.noisedetectionConfig(method='lundeby',compensatenoise=False)
#%% EMPTY
band = 1600

isotropy = {}
for key,d in zip(_datadicts.keys(),_datadicts.values()):
        print(yellow(key))
        pt_mtx = dsp.ifft_trunc(input_spk=d['pk'][:25,:],freq=d['freq'],
                                fs=d['fs'],
                                backend='cupy',
                                chunk_size=7
                                )

        pt_filt = EDCalc._filterSignal(pt_mtx,band=band,)
        EDC_mtx = EDCalc.integrate(pt_mtx, band=band, 
                        normalize=True,time_trunc=True)
        T20 = DirectionalDecay.get_nearest_T(material=key,band=band)        
        EDC_mtx = savgol(signal  = EDC_mtx, 
                         winsize = int(fs*(T20/12)),
                         axis    = -1,
                         backend = 'numpy',
                         chunk_size= 192
                         )

# %%
dB = lambda x: 10*np.log10(x + np.finfo(float).eps)
EDC_mtx /= np.max(abs(EDC_mtx),axis=-1,keepdims=True)

t = dsp.tvec(pt_filt.shape[1],fs)
t_E = dsp.tvec(EDC_mtx.shape[1],fs)
plt.plot(t, dB(pt_filt[0,:]**2))
plt.plot(t_E, dB(EDC_mtx[0,:]))
plt.axvline(max(t_E),color='black',linestyle='dashed')
plt.ylim(-80,None)
plt.title(f'{max(t_E):.5f} s')
