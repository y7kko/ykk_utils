#%%
import warnings
import numpy as np
from ykk_utils import dsp_funcs as dsp
# from ykk_utils import dsp_utils
from ykk_utils.arraybackends import ArrayBackendManager,ArrayBackendContext
from ykk_utils.arraybackends import array_slicetools as arrslice
import matplotlib.pyplot as plt

def lundeby_unvec(ht,fs,axis=-1,on_nonconvergence='raise'):
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
        
    dB = lambda x: 10*np.log10(x)    
    t = dsp.tvec(ht.shape[axis],fs)
    n_signals = ht.shape[not axis]

    crosspoint_instant = np.zeros(n_signals)
    C_comp = np.zeros(n_signals)
    
    with ArrayBackendContext('numpy') as yp:
        chk_size = int(10E-3*fs)
        ht_chk_mtx = yp.chunk_split2d(ht,chk_size=chk_size,discard_padded=True)
        ht_chk_mtx = np.sqrt(np.mean(ht_chk_mtx**2,axis=-1)) 
        
        t_chk_mtx = yp.chunk_split2d(t,chk_size=chk_size,discard_padded=True)
        t_chk_mtx = np.mean(t_chk_mtx,axis=-1)

    N_est_lim = int(t_chk_mtx.shape[axis]*.01)
    for idx in range(n_signals):
        # print(f'::: Index {idx}')
        sigslice= [slice(None)]*ht_chk_mtx.ndim
        sigslice[not axis]=idx
        ht_chk = ht_chk_mtx[tuple(sigslice)]
        t_chk = t_chk_mtx.copy()
        # print(ht_chk.shape)

        N_level = dB(np.mean(ht_chk[-N_est_lim:]**2))

        reg_idx = np.where(dB(ht_chk**2)>=(N_level+5))[0]
        reg_idx = np.where(reg_idx>=dB(ht_chk**2).argmax())[0]

        a,b = np.polyfit(x=t_chk[reg_idx], y=dB(ht_chk[reg_idx]**2),deg=1)

        # plt.plot(t_chk,dB(ht_chk**2))
        # plt.plot(t_chk,a*t_chk+b)
        dt = t_chk[1]-t_chk[0]
        idx_cross = int((N_level-b)/(a*dt))
        idx_cross = np.clip(idx_cross,0,len(t_chk))
        t_cross = t_chk[idx_cross]

        newint = -10/(3*a)
        # return

        # Second smoothing
        chk_size2 = int(newint*fs)
        ht_chk = dsp.chunk_split(ht[tuple(sigslice)],chk_size=chk_size2,discard_padded=True)
        ht_chk = np.sqrt(np.mean(ht_chk**2,axis=1))
        t_chk = dsp.chunk_split(t,chk_size=chk_size2,discard_padded=True)
        t_chk = np.mean(t_chk,axis=-1)
        
        tcross_cache = np.zeros(6)
        tcross_cache[0] = t_cross
        for iter in range(5):
            # print(f'   {iter}')
            #  Estima o nível 5dB acima de crosspoint
            # (a*t_cross+5)/a <- retorna t quando E(t) = (a*tcross + b) + 5
            dt = t_chk[1]-t_chk[0]
            N_est_idx = int(np.ceil((a*t_cross+5)/(a*dt)))
            if N_est_idx > (t_chk[-1]*.9)/dt:
                N_est_idx = int(np.ceil((t_chk[-1]*.9)/dt))
            N_level = dB(np.mean(ht_chk[N_est_idx:]**2))

            rlims = np.clip(a=  [
                                 np.floor((N_level+30-b)/(a*dt)),
                                 np.ceil((N_level+10-b)/(a*dt))
                                 ],a_min=0,a_max=len(t_chk)).astype(int)
            reg_idx = slice(rlims[0], rlims[1])
                
            # print((N_level+30-b)/(a*dt))
            a,b = np.polyfit(x=t_chk[reg_idx],y=dB(ht_chk[reg_idx]**2),deg=1)
            
            idx_cross = int((N_level-b)/(a*dt))
            idx_cross = np.clip(idx_cross,0,len(t_chk)-1)
            # old_tcross = np.copy(t_cross)
            tcross_cache[iter+1] = t_chk[idx_cross]

            # t_cross = t_chk[idx_cross]

            # plt.figure()
            # plt.plot(t_chk,dB(ht_chk**2))
            # plt.plot(t_chk,a*t_chk+b)
            # plt.axhline(N_level,linestyle='dashed',color='black')
            # plt.axvline(t_cross,linestyle='dashed',color='black')
            # plt.ylim([-120,0])
            # plt.title(f'iter {iter}')
            # plt.show()

            if abs(tcross_cache[iter]-tcross_cache[iter+1]) <= 0.01:
                crosspoint_instant[idx] = tcross_cache[iter+1]
                C_comp[idx] = np.sum(10**((a*t_chk[idx_cross:]+b)/10))
                break
        else:
            if on_nonconvergence == 'raise':
                raise RuntimeError(f'Signal at index {idx} did not converge after 5 iterations.')
            
            warnings.warn(f"Signal at index {idx} didn't converge")
            if on_nonconvergence == 'end':
                crosspoint_instant[idx] = t_chk[-1]
                # C_comp[idx] = np.sum(10**((a*t_chk[:-1]+b)/10))
                C_comp[idx] = 0
            elif on_nonconvergence == 'prelim':
                crosspoint_instant[idx] = tcross_cache[iter+1]
                C_comp[idx] = np.sum(10**((a*t_chk[idx_cross:]+b)/10))
            elif on_nonconvergence == 'mean':
                crosspoint_instant[idx] = np.mean(tcross_cache)
                idx_cross = abs(t_chk-crosspoint_instant[idx]).argmin()
                C_comp[idx] = np.sum(10**((a*t_chk[idx_cross:]+b)/10))

    return crosspoint_instant.squeeze(), C_comp.squeeze()
