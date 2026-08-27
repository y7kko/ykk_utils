#%%
import numpy as np
import matplotlib.pyplot as plt
from ykk_utils import dsp_funcs as dsp,EnergyDecayCalculator

def noise(length):
    """ White noise generator: [-1,1)
    """
    return (np.random.rand(length)-.5)*2
fs = 44100
eps = np.finfo(float).eps
EDCalc = EnergyDecayCalculator().filterConfig(fs=44100,nthoct=3)
dB = lambda x: 10*np.log10(x + eps)
#%%
NFFT = 2**19
t =dsp.tvec(NFFT,fs)
h = np.zeros([2,NFFT])

bgn = noise(NFFT)*(16E-4)*(2**3)

# Case 1: Multiexponential decay
h[0] = bgn + noise(NFFT)*np.exp(-1.2*t) + .5*noise(NFFT)*np.exp(-1.5*t)
# Case 2: Perfectly exponential decay
h[1] = bgn + noise(NFFT)*np.exp(-.74*t)

# plt.plot(t,dB(h**2))
# %%
band = 1E3
hf = EDCalc._filterSignal(h,band)
EDCalc.noisedetectionConfig(method='lundeby',compensatenoise=False)
tc = EDCalc._get_lundeby_tc(hf,headroom=0,plot_iters=True)
E = EDCalc.integrate(h,band,normalize=True,headroom=0)
E /= abs(E).max()
#%%
plt.title('Case 1: Multiexponential')
plt.plot(t,dB(hf[0]**2),label='$h^2(t)$')
t_e = dsp.tvec(E[0],fs)
plt.plot(t_e,dB(E[0]),label='EDC ')
plt.ylim(-80,None)
# plt.xlim(None,6)
plt.axvline(tc[0],color='black',linestyle='dashed')
plt.grid()
plt.legend()
#%%
plt.title('Case 2: Perfectly Exponential')
plt.plot(t,dB(hf[1]**2),label='$h^2(t)$')
t_e = dsp.tvec(E[1],fs)
plt.plot(t_e,dB(E[1]),label='EDC')
plt.ylim(-80,None)
plt.xlim(None,6)
plt.axvline(tc[0],color='black',linestyle='dashed')
plt.grid()
plt.legend()
# %%
