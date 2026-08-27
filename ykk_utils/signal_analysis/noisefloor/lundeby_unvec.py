#%%
import warnings
import numpy as np
from ykk_utils import dsp_funcs as dsp
# from ykk_utils import dsp_utils
from ykk_utils.arraybackends import ArrayBackendManager,ArrayBackendContext
from ykk_utils.arraybackends import array_slicetools as arrslice
import matplotlib.pyplot as plt

def lundeby_unvec(ht,fs,axis=-1,headroom=0,time_criterion=.5,maxiter=5,on_nonconvergence='raise',plot_iters=False):
    """Detecção de cauda de ruído

    Args:
        ht (_type_): _description_
        fs (_type_): _description_
        axis (int, optional): _description_. Defaults to -1.
        on_nonconvergence : str, default='raise'
            Comportamento quando o algoritmo não converge:
            - 'raise' : levanta RuntimeError
            - 'end'   : retorna o último instante da curva e constante de compensação zero
            - 'prelim': retorna o ponto de cruzamento preliminar
            - 'mean': O ponto de cruzamento é a média das iterações

    Returns:
        _type_: _description_
    """
    if ht.ndim ==1:
        ht = ht.reshape(1,-1)
        

    t = dsp.tvec(ht.shape[axis],fs)
    n_signals = ht.shape[not axis]

    crosspoint_instant = np.zeros(n_signals)
    C_comp = np.zeros(n_signals)
    
    chk_size = int(25E-3*fs)
    ht_chk_mtx,t_chk_mtx = _average_signal(ht,t,chk_size)

    N_est_lim = int(t_chk_mtx.shape[axis]*.01)
    non_convergent_indexes = np.zeros(n_signals)
    for idx in range(n_signals):
        # print(f'::: Index {idx}')
        sigslice= [slice(None)]*ht_chk_mtx.ndim
        sigslice[not axis]=idx
        ht_chk = ht_chk_mtx[tuple(sigslice)]
        t_chk = t_chk_mtx.copy()
        # print(ht_chk.shape)

        N_level = _dB(np.mean(ht_chk[-N_est_lim:]**2))

        reg_idx = np.where(_dB(ht_chk**2)>=(N_level+10))[0]
        reg_idx = np.where(reg_idx>=_dB(ht_chk**2).argmax())[0]

        a,b = np.polyfit(x=t_chk[reg_idx], y=_dB(ht_chk[reg_idx]**2),deg=1)

        dt = t_chk[1]-t_chk[0]
        idx_cross = int((N_level-b)/(a*dt))
        idx_cross = np.clip(idx_cross,0,len(t_chk)-1)
        t_cross = t_chk[idx_cross]
        if plot_iters:
            plt.figure()
            plt.title(f'{idx} - prelim')
            plt.plot(t_chk,_dB(ht_chk**2))
            plt.plot(t_chk,a*t_chk+b)
            plt.axvline(t_cross,color='black')
            plt.ylim(_dB(ht_chk**2).min()-10,None)

        newint = -10/(8*a)
        chk_size = int(newint*fs)
        ht_chk,t_chk = _average_signal(ht[tuple(sigslice)],t,chk_size)
        
        tcross_cache = np.zeros(6)
        tcross_cache[0] = t_cross

        for iter in range(maxiter):

            t_cross,a,b = _iterate(ht_chk,t_chk,
                                   tc=tcross_cache[iter],
                                   old_a=a,old_b=b
                                   )
            if plot_iters:
                plt.figure()
                plt.title(f'{idx} - iter {iter}')
                plt.plot(t_chk,_dB(ht_chk**2))
                plt.plot(t_chk,a*t_chk+b)
                plt.axvline(t_cross,color='black')
                plt.ylim(_dB(ht_chk**2).min()-10,None)
            tcross_cache[iter+1] = t_cross

            if abs(tcross_cache[iter]-tcross_cache[iter+1]) <= time_criterion:
                tc = tcross_cache[iter+1]
                crosspoint_instant[idx] = _find_above_headroom(ht_chk,t_chk,tc,headroom)
                break
        else:
            non_convergent_indexes[idx] = 1
            if on_nonconvergence == 'raise':
                raise RuntimeError(f'Signal at index {idx} did not converge after 5 iterations.')


            # warnings.warn(f"Signal at index {idx} didn't converge")
            if on_nonconvergence == 'end':
                tc = t_chk[-1]
            elif on_nonconvergence == 'prelim':
                tc = tcross_cache[0]
            elif on_nonconvergence == 'mean':
                tc = np.mean(tcross_cache[1:])
            elif on_nonconvergence == 'last':
                tc = tcross_cache[-1]

        crosspoint_instant[idx] = _find_above_headroom(ht_chk,t_chk,tc,headroom)
    if np.sum(non_convergent_indexes) != 0:
        print(f'These signals did not converge: {np.where(non_convergent_indexes==1)[0]}')
    return crosspoint_instant.squeeze()


def _update_mean(old_mean,old_size,new_val,append_size):
    new_size = old_size + append_size
    new_mean = (old_mean*old_size + new_val)/new_size
    return new_mean, new_size

def _find_above_headroom(ht_chk,t,tc,headroom):
    idx = abs(t-tc).argmin()
    obj_level = (10*np.log10(np.mean(ht_chk[idx:]**2))
                 + headroom)
    
    ht_idx = np.where(_dB(ht_chk**2)>=obj_level)[0]
    return t[ht_idx.max()]

def _clip_to_length(indexes,vector):
    indexes = np.asarray(indexes)
    rlims = np.clip(a=indexes,a_min=0,a_max=len(vector)-1).astype(int)
    return rlims

def _iterate(ht_chk,t_chk,tc,old_a,old_b):
    dt = t_chk[1]-t_chk[0]
    #  Estima o nível 5dB acima de crosspoint
    # (a*t_cross+5)/a <- retorna t quando E(t) = (a*tcross + b) + 5
    N_est_idx = int(np.ceil((old_a*tc+10)/(old_a*dt)))
    if N_est_idx > int((t_chk[-1]*.9)/dt):
        N_est_idx = int(np.ceil((t_chk[-1]*.9)/dt))
    N_level = _dB(np.mean(ht_chk[N_est_idx:]**2))

    rlims = _clip_to_length([
                            np.floor((N_level+30-old_b)/(old_a*dt)),
                            np.ceil((N_level+10-old_b)/(old_a*dt))
                            ],t_chk)
    reg_idx = slice(rlims[0], rlims[1])
        
    new_a,new_b = np.polyfit(x=t_chk[reg_idx],y=_dB(ht_chk[reg_idx]**2),deg=1)    
    idx_cross = _clip_to_length(int((N_level-new_b)/(new_a*dt)),t_chk)

    return t_chk[idx_cross],new_a,new_b


def _dB(x): 
    return 10*np.log10(x)


def _average_signal(ht,t,chk_size):
    with ArrayBackendContext('numpy') as yp:
        ht_avg = yp.chunk_split2d(ht,chk_size=chk_size,discard_padded=True)
        ht_avg = np.sqrt(np.mean(ht_avg**2,axis=-1)) 
        t_avg = yp.chunk_split2d(t,chk_size=chk_size,discard_padded=True)
        t_avg = np.mean(t_avg,axis=-1)

    return ht_avg,t_avg
