import numpy as np
import matplotlib.pyplot as plt

from ykk_utils.signal_analysis import dsp_funcs as dsp
from ykk_utils.special_methods.SHMatrix import SHMatrixProcessor
from ykk_utils import ykplot
from ykk_utils import dsputils
# import os
# from ykk_utils.special_methods import sh_operations as shops
# from ykk_utils.signal_analysis.smoothing import savgol


def plot_map(EDC,d00,dir,thresh=0,clims=[-9,9],cmap='RdBu'): 
    d00 = dsputils.norm_max(abs(d00))
    EDC = dsputils.norm_max(EDC)
    thresh_idx = abs(dsputils.dB(d00)-thresh).argmin()

    ykplot.figgen(4,2,1.2);

    inp = EDC[:,thresh_idx]/d00[thresh_idx]
    map = ykplot.plot_map(dir=dir,p=dsputils.dB(inp),
                        cmap=cmap,
                        vmin=clims[0],vmax=clims[1]
                        )

    plt.colorbar(map,label=r'$10 \log_{10}\left(d(t,\theta,\phi)/|d_{00}(t)|\right)$')


def nm_specgram(SHinstance:SHMatrixProcessor,t_sh=None,
                fs=None,x_is_dB=True,clims=[-15,0]):
    shp = SHinstance
    nmmap = shp.nmmap # Par (n,m)
    nmpair = np.arange(nmmap.shape[0]) #indices de cada (n,m)
    plt.figure(figsize=(7,3))
    SHDEDC = shp.SH_decomp
    # SHDEDC = dsputils.norm_max(abs(SHDEDC))
    # t_idx = np.arange(SHDEDC.shape[1])
    pc = plt.pcolormesh(t_sh,
                        nmpair,
                        dsputils.dB(abs(SHDEDC)/abs(SHDEDC[0,:])),
                        cmap='inferno',
                        vmin=-15,vmax=0
                        )
    #6+1 = Ordem máxima
    N0_indexes = np.zeros(nmmap[:,0].max()+1) 
    N0_lim = np.zeros(nmmap[:,0].max()+1) #6+1(Ordem máxima)

    for idx in range(len(N0_indexes)):
        N0_indexes[idx] = np.where((nmmap[:,0] == idx) & (nmmap[:,1] == 0))[0]
        N0_lim[idx] = np.where((nmmap[:,0] == idx) & (nmmap[:,1] == idx))[0]

    plt.yticks(N0_indexes,list(f'$A_{{{N},0}}$' for N in range(len(N0_indexes))));
    for idx_0,idx_lim in zip(N0_indexes,N0_lim):
        plt.axhline(idx_0,linestyle='dashed',alpha=.5);
        plt.axhline(idx_lim,linestyle='dotted',alpha=.5);


    plt.colorbar(pc,label=r'$d_{nm}(t)/d_{00} \quad\mathrm{(dB)}$')
    plt.xlabel('Tempo (s)')
    plt.ylabel('(n,m)')
    plt.ylim(1,None)
