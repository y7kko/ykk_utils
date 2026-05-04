import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from ykk_utils.signal_analysis_utilities import dsp_funcs as dsp
import ykk_utils.signal_analysis_utilities.dsp_funcs as dsp
from .NominalFractionalBands import ThirdOctaveBands, OctaveBands

class FractionalFilter:
    def __init__(self,fs,nthoct=1,minfreq=20,maxfreq=19.9E3,order=10,fref=1E3,autofix=True):
        """Implementa filtros de bandas fracionárias conforme IEC 61260-1:2014

        Args:
            fs:
            nthoct (int, optional): 
                Designador de largura de banda(1/b). 
                nthoct=3 gera um filtro de terço de oitava,  por exemplo. 
                Defaults to 1.
            minfreq (float, optional): Frequência mínima(que quero analisar). Defaults to 20.
                minfreq e maxfreq servem para procurar as bandas que englobam essa faixa. Caso
                a banda que engloba maxfreq ultrapasse nyquist(fs/2), essa banda é descartada. 
            maxfreq (float, optional): Frequência máxima(que quero analisar). Defaults to 20E3.
        """
        self.G      = 10**(3/10) # Octave frequency ratio
        self.fref   = fref #Na IEC é sempre 1k, mas faz bem ser alteravel
        self.nthoct = nthoct
        self.filter_order = order
        self.fs = fs
        
        # Funções para banda fracionária
        self.f_center_calculator = self.get_midfreq_expression(nthoct)

        # G^{x/b}
        x_min, x_max = self._x_minmax(freqlims=[minfreq,maxfreq],
                                      b=nthoct,
                                      fr=self.fref)
        
        self.x = np.arange(x_min,x_max+1) # 

        self.f_center = self.f_center_calculator(self.x)

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

        self.f_nominal = self.get_nominal_freqs(nthoct)
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
            cf = cf[abs(self.f_center[0]-cf).argmin():abs(self.f_center[-1]-cf).argmin()]
        elif b == 3:    # Anexo E.1
            cf = ThirdOctaveBands.center_freqs()
            cf = cf[abs(self.f_center[0]-cf).argmin():abs(self.f_center[-1]-cf).argmin()]
        elif b == 2:    # Anexo E.2
            cf = self.f_center.round(3)
        else:           # Anexo E.3
            cf = self.f_center.copy()
            #Essa expressão deveria obter o primeiro dígito significativo
            left_vals = np.floor(cf / (10 ** np.floor(np.log10(cf)))).astype(int)
            for idx in range(len(left_vals)):
                if left_vals[idx]<=4:
                    cf[idx] = cf[idx].round(3)
                else:
                    cf[idx] = cf[idx].round(2)

        return cf

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

    def filter(self, input, band = None, axis=None):
        """Filtra um sinal(ou múltiplos sinais) de entrada. Caso
        input tenha ndims > 1, será necessário especificar um axis

        Args:
            input (ndarray): O sinal a ser filtrado
            band (float,ndarray,list, optional): Especifica quais bandas retornar:
                - Caso None: Retorna o sinal filtrado em todas as bandas. 
                - Caso escalar: Retorna o sinal filtrado na banda mais próxima
                    da frequência especificada
                - Caso uma lista: Retorna o sinal filtrado nas respectivas 
                    bandas mais próximas especificadas na lista. Defaults to None.
            axis (int, optional): O eixo temporal(Caso axis = None, axis é overwritten para -1). 
                Defaults to None.


        Returns:
            ndarray: Vetor de entrada filtrado em bandas. A saida
                possui shape [n_bands, *input_shape]
        """
        # 22/04: Achei uma solução elegante, vamo ver se dura
        if band is None: 
            sos_mtx = self.sos_mtx
        elif np.isscalar(band): 
            idx = abs(self.f_nominal-band).argmin()
            sos_mtx = self.sos_mtx[idx,:,:].reshape([1,self.filter_order,6])
        else: 
            idx = np.array(
                list( abs(self.f_nominal - f).argmin() for f in band )
                ).sort()
            sos_mtx = self.sos_mtx[idx,:,:]
        #Axis = None é undefined behaviour em sosfilt
        if axis is None:
            axis = -1

        # list unwrap e depois wrap dnv
        output = np.zeros( [sos_mtx.shape[0], *list(input.shape)] )
        for b_idx in range(output.shape[0]):
            output[b_idx] = signal.sosfilt(sos=sos_mtx[b_idx,:,:],
                                            x=input,
                                            axis=axis)

        return output
