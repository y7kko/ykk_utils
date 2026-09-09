#%%
import numpy as np
import matplotlib.pyplot as plt
from ykk_utils import dsp_funcs as dsp
from ykk_utils.applications.DirectionalDecay import DEDCCalculator

def noise(length):
    """ White noise generator: [-1,1)
    """
    return (np.random.rand(length)-.5)*2
fs = 44100
eps = np.finfo(float).eps
EDCalc = DEDCCalculator().filterConfig(fs=44100,nthoct=3)
dB = lambda x: 10*np.log10(x + eps)


def artificial_edc(T60,fs,length,amplitude=1):
    # time_constant = 13.8/T60
    time_constant = 6.908/T60
    NFFT= int(fs*length)
    t = dsp.tvec(NFFT,fs)
    E  = noise(NFFT)
    E *= amplitude*np.exp(-time_constant*t) #(Balint, et al) eq 1
    return E

def artificial_residual(level,fs,length):
    amplitude = 10**(level/20)
    NFFT= int(fs*length)
    return noise(NFFT)*amplitude

# def curvature_estimator(EDC,t):
#     from ykk_utils.applications import room_acoustics 
#     T20 = room_acoustics.T20(EDC,time=t,)
#     T30 = room_acoustics.T30(EDC,time=t,)
#     return 100*((T30/T20) - 1)
def curvature_estimator(EDC,t):
    from ykk_utils.applications import room_acoustics 
    T15 = room_acoustics.RT._Tn(EDC,time=t,decayLevel=15)
    T20 = room_acoustics.T20(EDC,time=t,)
    return 100*((T20/T15) - 1)
#%%
length = 15 #s
NFFT = int(15*fs)
t =dsp.tvec(NFFT,fs)

#%%

h_1 = artificial_edc(7,fs,length)
h_1 += artificial_residual(-60,fs,length)

tc = EDCalc._get_lundeby_tc(h_1,0)
E_1 = EDCalc._rcumsum_crop(h_1**2,t,tc,normalize=True)
score = curvature_estimator(dB(E_1),t)
plt.plot(t,dB(h_1**2))
plt.plot(t,dB(E_1))
plt.ylim([-60,0])
plt.axvline(tc,color='black',linestyle='dashed')
plt.title(f'curvature score {score}')
# %%
h_2 = artificial_edc(2,fs,length,1)
h_2 += artificial_edc(7,fs,length,.25)
h_2 /= abs(h_2).max()
h_2 += artificial_residual(-60,fs,length)

tc = EDCalc._get_lundeby_tc(h_2,0)
E_2 = EDCalc._rcumsum_crop(h_2**2,t,tc,normalize=True)
score = curvature_estimator(dB(E_2),t)
plt.plot(t,dB(h_2**2))
plt.plot(t,dB(E_2))
plt.ylim([-60,0])
plt.axvline(tc,color='black',linestyle='dashed')
plt.title(f'curvature score {score}')
# %%
