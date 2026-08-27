#%%
import numpy as np
from ykk_utils import ThirdOctaveBands
from ykk_utils.signal_analysis.error_funcs import Efren

def _MAE(x_sol,x_truth,axis=-1):
    num = abs(x_truth-x_sol).sum(axis=axis)
    den = x_sol.shape[axis]
    return num/den 

def _NMSE(x_sol,x_truth,axis=-1):
    num = np.linalg.norm(x_truth-x_sol, axis=axis)
    den = np.linalg.norm(x_truth, axis=axis)
    return num/den

def _MSE(x_sol,x_truth,axis=-1):
    """||x-\hat{x}||^2_2/N

    """

    num = np.linalg.norm((x_truth-x_sol), axis=axis)**2
    return num/x_sol.shape[axis]

def _RMSE(x_sol,x_truth,axis=-1):
    return np.sqrt(_MSE(x_sol=x_sol,
                        x_truth=x_truth,
                        axis=axis
                        )
                    )
def _NRMSE(x_sol,x_truth,axis=-1):
    """ Baseado na defnição que encontrei aqui
    https://ar5iv.labs.arxiv.org/html/2207.07091#3
    """
    RMSE = _RMSE(x_sol=x_sol,x_truth=x_truth,axis=axis)
    norm_max = np.max(abs(x_truth),axis=axis,keepdims=True)
    return RMSE/(norm_max)

    pass
_recerr_funcs= {
    'NMSE':_NMSE,
    'MAE': _MAE,
    'MSE': _MSE,
    'RMSE': _RMSE,
    'NRMSE': _NRMSE,
                }

class ReconstructionError:
    def __init__(self,x_sol,x_truth,freq):
        self.x_sol = x_sol
        self.x_truth = x_truth
        self.freq = freq

    def calculate_err(self,metric='NMSE'):
        self.err = _recerr_funcs[metric.upper()](x_sol=self.x_sol,
                                         x_truth=self.x_truth,
                                         axis=0).squeeze()
        return self.err

    def mean_err(self,fminmax=[None,None],kind='third'):
        if not hasattr(self,'err'):
            self.calculate_err();

        if len(fminmax) != 2:
            raise ValueError('fminmax deve ser uma lista com dois valores (mínimo, máximo)')
        if fminmax[0] is None:
            fminmax[0] = self.freq.min()
        if fminmax[1] is None:
            fminmax[1] = self.freq.max()

        fc = ThirdOctaveBands.center_freqs(freq_lims=fminmax)
        fcl = ThirdOctaveBands.minmax_freqs(freq_lims=fminmax)
        err_third = np.zeros(fc.shape)
        for idx,(minfreq,maxfreq) in enumerate(zip(fcl[:,0],fcl[:,1])):
            f_idx = np.where((self.freq>=minfreq) & (self.freq <= maxfreq))
            err_third[idx] = np.mean(self.err[f_idx])
        return fc, err_third

