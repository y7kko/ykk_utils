import numpy as np
from . import RT_core
from ykk_utils.arraybackends import cross_slice2d

def T20(edc,time,axis=-1):
    n_meas = edc.shape[not axis]
    TR_arr = np.zeros(n_meas)
    for idx in len(n_meas):
        a,b = RT_core.tr_fit(edc,time,Ldecay=20,Lstart=-5)
        TR_arr[idx] = RT_core.tr_extrapolate(a,b)
    return TR_arr

def T30(edc,time,axis=-1):
    n_meas = edc.shape[not axis]
    TR_arr = np.zeros(n_meas)
    for idx in len(n_meas):
        a,b = RT_core.tr_fit(edc,time,Ldecay=30,Lstart=-5)
        TR_arr[idx] = RT_core.tr_extrapolate(a,b)
    return TR_arr

