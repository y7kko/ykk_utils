import pytta
import numpy as np
import matplotlib.pyplot as plt
import random
from ppro_meas_insitu import InsituMeasurementPostPro
import os
from matplotlib.collections import LineCollection

def compare_noise(ppro_obj:InsituMeasurementPostPro):
    """todo: Transformar isso num codigo de vdd. Fazer uma função auxiliar para varrer a pasta
    e retornar todos os filenames que match, fazer uma função que injeta .load_signal()

    Args:
        ppro_obj (InsituMeasurementPostPro): _description_
    """
    noise_at_each = 2
    ir = ppro_obj.load_signal(f'noise{1}')

    n_pts = ppro_obj.meas_obj.receivers.coord.shape[0]
    n_spl = len(ir.timeVector)
    noise_mtx = np.zeros([int(n_pts/noise_at_each), n_spl])
    for mtx_idx,index in enumerate(np.arange(1,n_pts,noise_at_each)):
        noise_mtx[mtx_idx,:] = ppro_obj.load_signal(f'noise{index}').timeSignal[:,0]
    noise_rms = np.mean(np.abs(noise_mtx)**2,axis=1)
    
    ir = ppro_obj.load_signal(f'rec0_m0')[0]
    n_pts = ppro_obj.meas_obj.receivers.coord.shape[0]
    n_spl = len(ir.timeVector)
    noise_mtx_rec = np.zeros([n_pts, n_spl])

    for idx in range(n_pts):
        noise_mtx_rec[idx,:] = ppro_obj.load_signal(f'rec{idx}_m0')[0].timeSignal[:,0]
    noise_rms_rec = np.mean(np.abs(noise_mtx)**2,axis=1)
    # ppro_obj.load_irs()
    
    start_idx = noise_mtx_rec.shape[1]-int(noise_mtx_rec.shape[1]*0.01) - 1
    noisy_ht = noise_mtx_rec[:,start_idx:]
    noise_rms_yt = np.mean(np.abs(noisy_ht)**2,axis=1)
    
    plt.plot(10*np.log10(noise_rms_yt),label="y(t = [90%:100%] )")
    plt.plot(np.arange(1,n_pts,noise_at_each),10*np.log10(noise_rms),label='Noise recording')
    plt.xlabel("Indice de medição")
    plt.ylabel("Energia do sinal (dB)")
    plt.grid()
    plt.legend()
