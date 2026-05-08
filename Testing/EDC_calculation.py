#%%
from ykk_utils.signal_analysis_utilities import EnergyDecayAnalyser as _EDC
from ykk_utils.signal_analysis_utilities import dsp_funcs as dsp
import numpy as np
import matplotlib.pyplot as plt
def noise(length):
    return np.random.rand(length)*2-1

#%%

fs = 48E3
nfft = 2**20
a = 1.5
t = dsp.tvec(nfft,fs)
aex = [1,0]

ht = (  aex[0]*noise(nfft)*np.exp(-a*t)  #primeiro decaimento
      + aex[1]*noise(nfft)*np.exp(-3.14*a*t) #segundo decaimento 
      + 1E-2*noise(nfft) #noise floor
      )
ht /= max(abs(ht))


ht = ht[0:round(len(ht)/2)]
t = t[0:len(ht)]

EAN = _EDC.EDCAnalyser().filterConfig(fs)
edc = EAN.EDC(band=1000,input=ht)

#!%%
plt.plot(t,10*np.log10(ht**2),label='$h^2(t)$')
plt.plot(t,10*np.log10(edc),label="EDC($t$)")
plt.ylim(-50,0)
