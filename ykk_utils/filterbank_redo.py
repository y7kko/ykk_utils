#%%
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from ykk_utils.signal_analysis_utilities import dsp_operations as dsp
from ykk_utils import ThirdOctaveBands,OctaveBands

# JUST FOR DATAVIZ AND TESTING
import pandas as pd
import pytta

#!%%
class FractionalFilter:
    def __init__(self,fs,nthoct=1,minfreq=20,maxfreq=19.9E3,order=10,fref=1E3,autofix=True):
        """Implementa filtros de bandas fracionárias conforme IEC 61260-1:2014

        Args:
            nthoct (int, optional): 
                Designador de largura de banda(1/b). 
                nthoct=3 gera um filtro de terço de oitava,  por exemplo. 
                Defaults to 1.
            minfreq (float, optional): Frequência central mínima. Defaults to 20.
            maxfreq (float, optional): Frequência central máxima. Defaults to 20E3.
        """
        self.G      = 10**(3/10) # Octave frequency ratio
        self.fref   = fref
        self.nthoct = nthoct
        self.filter_order = order
        self.fs = fs
        
        # Funções para banda fracionária
        self.f_center_function = self.get_midfreq_expression(nthoct)

        # G^{x/b}
        x_min, x_max = self._x_minmax(freqlims=[minfreq,maxfreq],
                                      b=nthoct,
                                      fr=self.fref)
        
        self.x = np.arange(x_min,x_max+1) # 

        self.f_center = self.f_center_function(self.x)

        self.f_lims = np.array([
            (self.f_center)*self.G**(-1/(2*self.nthoct)),
            (self.f_center)*self.G**(+1/(2*self.nthoct))
            ]).T
        
        if autofix:
            #Remove as bandas em que não posso projetar um filtro por conta do fs
            idx = np.where(self.f_lims[:,1]< (self.fs/2))[0]
            self.f_center = self.f_center[idx]
            self.f_lims= self.f_lims[idx,:]
            self.x = self.x[idx]
            # Formula empirica pra dar uma puxada pra frequência centrla

        self.nominal_freqs = self.get_nominal_freqs(nthoct)
        self.generate_sos_matrix()
        

    def generate_sos_matrix(self):
        """Gera a matriz de seções de segunda ordem (biquad -- iir)

        ## Nota para o Bruno do futuro:
            O formato SOS retorna em um vetor [N/2,6] os coeficientes a e b de um filtro iir 
            de segunda ordem(em que N é a ordem do filtro). A expressão para uma única seção
            de segunda ordem é:
                `a0·y[n] = b0·x[n] + b1·x[n-1] + b2·x[n-2] - a1·y[n-1] - a2·y[n-2]`
                
                com `a0 = 1` sempre. Note que filtros de ordem superior consistem em 
                reaplicar essa expressão em cascata (H1(jw)*H2(jw)*...*Hn(jw))

            No caso de um filtro passa-banda de ordem N, ele é composto de dois filtros: 
            um passa-baixa de ordem N e outro passa-alta de ordem N, resultando em um 
            filtro de ordem 2N. Portanto, o vetor SOS para um btype='bp' possui 
            tamanho [(2/2)*N,6]=[N,6].

        """
        n_bands =len(self.f_center)
        sos_mtx = np.zeros([n_bands,self.filter_order,6])

        for band_idx in range(n_bands):
            f_minmax = self.f_lims[band_idx,:]
            sos = signal.butter(N=self.filter_order,
                                Wn=f_minmax, fs=self.fs,
                                btype='bp', output='sos',
                                )
            sos_mtx[band_idx,:,:] = sos

        self.sos_mtx = sos_mtx


    def get_midfreq_expression(self,b):
        """Retorna uma função para cálculo da
        frequência central correspondente ao designador de largura de banda(1/b).
        
        Essa função implementa as Equações (2) e (3) da Norma

        Args:
            b (int): fração de oitava

        Returns:
            callable: função para calculo das freqyêbcuas centraisa
        """
        if b % 2:
            fm_exp =lambda x: self.fref * self.G**(x/b)
        else:
            fm_exp =lambda x: self.fref * self.G**((2*x+1)/(2*b))

        return fm_exp

    def get_nominal_freqs(self,b):
        """Simplesmente revoltante, mas isso implementa o Anexo E da norma...
            
            
            Ainda não testei, btw...
        Args:
            freqlims (_type_): _description_
            b (_type_): _description_

        Returns:
            _type_: _description_
        """
        if b == 1:      # Anexo E.1
            cf= OctaveBands.center_freqs() #Pode ser substituido por uma lista btw
            cf = cf[abs(self.f_center[0]-cf).argmin():abs(self.f_center[-1]-cf).argmax()]
            return cf
        elif b == 3:    # Anexo E.1
            cf = ThirdOctaveBands.center_freqs()
            cf = cf[abs(self.f_center[0]-cf).argmin():abs(self.f_center[-1]-cf).argmax()]
            return cf
        elif b == 2:    # Anexo E.2
            return self.f_center.round(3)
        else:           # Anexo E.3
            bfreq = self.f_center.copy()

            #Essa expressão deveria obter o primeiro dígito significativo
            left_vals = np.floor(bfreq / (10 ** np.floor(np.log10(bfreq)))).astype(int)
            for idx in range(len(left_vals)):
                if left_vals[idx]<=4:
                    bfreq[idx] = bfreq[idx].round(3)
                else:
                    bfreq[idx] = bfreq[idx].round(2)
                return bfreq


    @staticmethod
    def _x_minmax(freqlims,b,fr):
        """Calcula os valores minimos e máximos de x(numerador da potência).
        Essa função é uma inversão das Equações (2) e (3) da norma.

        Args:
            freqlims (_type_): _description_
            b (_type_): _description_
            fr (_type_): _description_

        Returns:
            _type_: _description_
        """
        f_min = freqlims[0]
        f_max = freqlims[1]

        if b%2:
            x = lambda fm: ((10*b/3)*np.log10(fm/fr))
        else:
            x = lambda fm: (20*b*np.log10(fm/fr)-3)/6


        # Acho que tem vezes que não vai funcionar, não sei como abordar...
        x_min = int(np.round(x(f_min) + 1e-12))
        x_max = int(np.round(x(f_max)))
        
        return x_min, x_max



    def filter(self, input, band = None, axis=-1):

        # 22/04: Achei uma solução elegante, vamo ver se dura
        if band is None: 
            sos_mtx = self.sos_mtx
        elif np.isscalar(band): 
            idx = (self.nominal_freqs-band).argmin()
            sos_mtx = self.sos_mtx[idx,:,:].reshape([1,self.filter_order,6])
        else: 
            idx = np.array(
                list( (self.nominal_freqs - f).argmin() for f in band )
                ).sort()
            sos_mtx = self.sos_mtx[idx,:,:]

        # list unwrap e depois wrap dnv
        output = np.zeros( [sos_mtx.shape[0], *list(input.shape)] )
        for b_idx in range(output.shape[0]):
            output[b_idx] = signal.sosfilt(sos=sos_mtx[b_idx,:,:],
                                            x=input,
                                            axis=axis)

        return output

#%%
fs = 44100
imp = pytta.generate.impulse(samplingRate=fs,fftDegree=19)
sig_y = imp.timeSignal.T[0]
sig_t = imp.timeVector
#%%
filter = FractionalFilter(fs=fs,nthoct=3,order=10)

#%%
sig_y_f = filter.filter(sig_y)

#%%

sig_yjw = np.fft.rfft(sig_y)
f = dsp.generate_frequency_vector(fs,len(sig_yjw)*2,half_spectrum=True)
ax = plt.plot(f,20*np.log10(abs(sig_yjw)),label="$x(t)$ 2",color='gray')
plt.legend(['$x(t)$'],loc='lower center')

for sig_idx in range(sig_y_f.shape[0]):
    sigjw = np.fft.rfft(sig_y_f[sig_idx,:])
    f = dsp.generate_frequency_vector(fs,len(sigjw)*2,half_spectrum=True)
    plt.plot(f,20*np.log10(abs(sigjw)+1E-12))

plt.ylim([-3,1])
plt.xscale('log')
plt.xlim(10,25E3)

for val,nom in zip(filter.f_center,filter.nominal_freqs):
    l = plt.axvline(val,color='#55555555',linestyle='--')
    plt.text(x=val,y=plt.ylim()[1]-.75,s=f'{nom:.1f} Hz',rotation=90,color="#555555")

plt.xticks(*[OctaveBands.center_freqs([14,20E3])]*2,rotation=45);
plt.grid()

#%%
import pandas as pd

display(pd.DataFrame(dict(
                  fc=filter.f_center,
                  fmin=filter.f_lims[:,0],
                  fmax=filter.f_lims[:,1])
                  ).round(2))
# print(np.array([filter.f_center, ]).T)
# 
print(len(filter.f_lims))
print((filter.nominal_freqs))
# %%
