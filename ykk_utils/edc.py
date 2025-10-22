import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from ppro_meas_insitu import InsituMeasurementPostPro
from matplotlib.collections import LineCollection
from .filterclass import OctFilter
from .FractionalBands import OctaveBands,ThirdOctaveBands

# import seaborn as sns


band_color = [
            'tab:blue',
            'tab:orange',
            'tab:green',
            'tab:red',
            'tab:purple',
            'tab:brown',
            'tab:pink',
            'tab:gray', 
            'tab:olive', 
            'tab:cyan'
            ]

class ykkEDC:
    """ Classe destinada a calcular as EDCs e realizar operações com elas
    """
    def __init__(self,ht_mtx=None, time = None, nthOct=3, minFreq=125, maxFreq=5E3, samplingRate=44100,base=10,order=6,refFreq=1000):
        """Classe dedicada a realizar operações com EDCs.

        Args:
            ht_mtx (numpy.ndarray): A matriz de impulse responses no formato [n_rec, time]
            nthOct (int, optional): A fração de oitava. Defaults to 1.
            minFreq (int, optional): Frequência mínima. Defaults to 125.
            maxFreq (_type_, optional): Frequência máxima. Defaults to 4E3.
            refFreq (int, optional): Frequência de referência. Defaults to 1000.
            base (int, optional): Base logaritmica, n sei pq mexeria. Defaults to 10.
            order (int, optional): Ordem dos filtros. Defaults to 6.
            samplingRate (int, optional): Taxa de amostragem do sinal. Defaults to 44100.
        """

        self.filter_obj = OctFilter(  nthOct=nthOct,
                            minFreq=minFreq,
                            maxFreq=maxFreq,
                            samplingRate=samplingRate,
                            base=base,
                            order=order,
                            refFreq=refFreq
                        )
        if ht_mtx is None:
            Warning("ht_mtx not initialized, some functions may not work properly")
        
        self.ht_mtx = ht_mtx
        self.band_freqs = self.filter_obj.get_band_freqs()
        if time == None:
            self.time = np.arange(0,
                                  ht_mtx.shape[1]/samplingRate,
                                  1/samplingRate
                                  )
        else:
            self.time = time



    def compute(self,):
        """Calcula as EDCs e retorna em uma matriz

        Returns:
            numpy.ndarray: Uma matriz de shape [n_rec, time, band] contendo a EDC (dB)
        """
        print(':: Filtering h(t)')
        self.ht_mtx_bp = self.filter_obj.filter_mtx(self.ht_mtx)
        
        self.EDC_mtx = np.zeros(self.ht_mtx_bp.shape)
        print(':: Calculating EDC\'s')
        progress_bar = tqdm(total=self.ht_mtx_bp.shape[0]*self.ht_mtx_bp.shape[2])
        for ir_idx in range(self.ht_mtx_bp.shape[0]):
            for band_idx in range(self.ht_mtx_bp.shape[2]):
                EDC_ir = self.computeEDC(
                            self.ht_mtx_bp[ir_idx,:,band_idx]
                        )
                self.EDC_mtx[ir_idx,:,band_idx] = EDC_ir
                progress_bar.update(1)
        
        return self.EDC_mtx

    def compute_all_tn(self,):
        progress_bar = tqdm(total=3)
        self.computeT20_mtx()
        progress_bar.update(1)
        self.computeT30_mtx()
        progress_bar.update(1)
        self.computeEDT_mtx()
        progress_bar.update(1)

    def computeT20_mtx(self,returncoefs=False):
        self.T20, self.T20_coefs = self.computeTn_mtx(start=-5, n=20)
        if returncoefs:
            return self.T20_coefs


    def computeT30_mtx(self,returncoefs=False):
        self.T30, self.T30_coefs = self.computeTn_mtx(start=-5, n=20)
        if returncoefs:
            return self.T30_coefs

    def computeEDT_mtx(self,threshold=1E-2,returncoefs=False):
        Warning("ainda não implementei essa bosta, falta achar o zero")
        self.EDT, self.EDT_coefs = self.computeTn_mtx(start=0-threshold, n=10)
        if returncoefs:
            return self.EDT_coefs


    def computeTn_mtx(self,**kwargs):
        """Computa o tempo de reverberação da matriz

        Returns:
            Tn_mtx: Matriz de tempo de reverberação [n_recs, n_bands]
            reg_coeffs_mtx: Matriz de coeficientes da reta [n_recs, 2 , n_bands]
        """
        reg_coeffs_mtx = np.zeros([self.EDC_mtx.shape[0], #n_rec 
                      2, # coeffs (a, b)
                      self.EDC_mtx.shape[2]] #band
                      )
        
        Tn_mtx = np.zeros([self.EDC_mtx.shape[0], #n_rec 
                          self.EDC_mtx.shape[2]] #band
                )
        for ir_idx in range(self.ht_mtx_bp.shape[0]):
            for band_idx in range(self.ht_mtx_bp.shape[2]):
                a,b = self.Tn(EDC = self.EDC_mtx[ir_idx,:,band_idx],
                                                    time = self.time,
                                                    **kwargs)
                reg_coeffs_mtx[ir_idx,:,band_idx] = [a,b]
                Tn_mtx[ir_idx,band_idx] = ( (-60) - b) / a # Equacao da reta

        return Tn_mtx, reg_coeffs_mtx

    #Computar o T20,T30, EDT

    @staticmethod
    def Tn(EDC, time, n=20, start = None,init_time=None):
        if init_time is None:
            if start == None:
                start = -5
            end = start - n

            indexes = np.where((EDC<=start) & (EDC>=end))
            # a*x + b
        else:
            t_idx = np.where(time>=init_time)
            indexes = np.where(EDC >= end)
            indexes = np.intersect1d(t_idx,indexes)

        a, b = np.polyfit(time[indexes], EDC[indexes], 1)
        return a, b
        
    @staticmethod
    def computeEDC(ir):
            """Calcula a EDC de uma curva

            Args:
                ir (numpy.ndarray): Uma resposta ao impulso

            Returns:
                numpy.ndarray: A EDC do sinal (dB)
            """
            EDC = np.cumsum(np.flipud(ir**2))
            EDC = np.flipud(EDC)/np.max(EDC) 
            return 10*np.log10(EDC)
    
    #Plotting routines
    def plot_all(self,ax=None,show_legend=True):
        ax = _PlotRoutines.get_axis(ax)

        ax.set_xlim(-0, 6)
        ax.set_ylim(-80, 0)

        _PlotRoutines.plot_EDC_mtx(time=self.time,
                                   EDC_mtx=self.EDC_mtx,
                                   label_list=[f'{band:.0f} Hz' for band in self.band_freqs],
                                   ax=ax,
                                   time_step=4
                                   )

        ax.grid()
        ax.set_ylabel('EDC (dB)')
        if show_legend:
            legend = ax.legend()
            for line in legend.get_lines(): #as EDCs possuem linewidth de 0.2
                line.set_linewidth(1.2)

    def plot_single_band_EDC(self,band ,ax=None,xlim=None,ylim=None,):
        """Plota todas as EDCs de uma banda específica

        Args:
            band (_type_): _description_
            ax (_type_, optional): _description_. Defaults to None.
            xlim (_type_, optional): _description_. Defaults to None.
            ylim (_type_, optional): _description_. Defaults to None.
        """
        ax = _PlotRoutines.get_axis(ax)

        if xlim is None:
            xlim = [0,self.time[-1]]
        if ylim is None:
            ylim = [-80,0]

        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        band_idx = np.argmin(np.abs(self.band_freqs - band))
        _PlotRoutines.plot_EDC_mtx(time=self.time,
                                   EDC_mtx=self.EDC_mtx[:,:,band_idx],
                                #    label_list=[f''],
                                   ax=ax,
                                   time_step=4
                                   )
        
    def plot_single_Tn(self,band,kind='T20' ,ax=None,xlim=None,ylim=None,):
        ax = _PlotRoutines.get_axis(ax)

        band_idx = np.argmin(np.abs(self.band_freqs - band))
        if kind == 'T20':
            Tn = np.mean(self.T20_coefs[:,:,band_idx],axis=0) #checar isso aqui

        ax.plot(self.time,Tn,label='$T_20$')



    def plot_edc_x_ht(self, index, band_freq = None,ax=None):
        if band_freq is None:
            ht = self.ht_mtx[index,:]
            EDC = self.computeEDC(ht)
        else:
            band_idx = np.argmin(abs(band_freq-self.band_freqs))
            ht = self.ht_mtx[index,:,band_idx]
            EDC = self.computeEDC(ht)
        
        ax = _PlotRoutines.get_axis(ax)

        ht2plot = ht**2
        ht2plot /= max(ht2plot)
        ht2plot = 10*np.log10(ht2plot)

        ax.plot(self.time,ht2plot,label="$h(t)$")
        ax.plot(self.time,EDC,label="EDC")

        ax.set_ylabel("Magnitude (dB)")
        ax.set_xlabel("Tempo (s)")
        
        return ax
    




class EDCinstancer:
    """Gera uma instância ykkEDC a partir de uma instância InsituMeasurementPostPro
    """
    @staticmethod
    def instance(ppro_obj:InsituMeasurementPostPro,**kwargs) -> 'ykkEDC':
        """Fabrica uma instância da classe ykkEDC a partir de um objeto de pós processamento

        Args:
            ppro_obj (InsituMeasurementPostPro): A classe de pós processamento com ht_mtx calculada

        Returns:
            ykk_utils.ykkEDC : Uma instância configurada da classe ykkEDC
        """

        #isso ainda desconsidera quando as irs não foram nem calculadas
        try: 
            input_matrix = ppro_obj.ht_mtx
        except:
            ppro_obj.load_irs()
            input_matrix = ppro_obj.ht_mtx

        return ykkEDC(ht_mtx=input_matrix,
                      samplingRate=ppro_obj.meas_obj.fs,
                      **kwargs)
    

class _PlotRoutines:
    """Classe interna para realizar plots
    """
    @staticmethod
    def plot_single_EDC():
        pass

    @staticmethod
    def plot_EDC_mtx(time,EDC_mtx:np.ndarray,label_list=None,time_step=1,ax=None):
        # fig, ax = plt.subplots(figsize=(6,4))
        n_bands = EDC_mtx.shape[2]
        ax = _PlotRoutines.get_axis(ax)


        if label_list is None:
            label_list = ['']*n_bands

        for band_idx in range(n_bands):
            band_EDC = [np.column_stack([time[::time_step], EDC_mtx[ir_idx,::time_step,band_idx]]) for ir_idx in range(EDC_mtx.shape[0])]
            line_collection = LineCollection(band_EDC,
                                            colors=band_color[band_idx],
                                            linewidths=0.2,
                                            label=label_list[band_idx],
                                            zorder=2,
                                            rasterized=True
                                            )
            ax.add_collection(line_collection)


    @staticmethod
    def faster_plot_EDC_mtx(time,EDC_mtx:np.ndarray,label_list=None,time_step=1,ax=None):
        global band_color
        ax = _PlotRoutines.get_axis(ax)


        n_bands = EDC_mtx.shape[2]
        if label_list is None:
            label_list = ['']*n_bands

        line_collections = [LineCollection]*n_bands

        for band_idx in range(n_bands):
            band_EDC = [np.column_stack([time[::time_step], EDC_mtx[ir_idx,::time_step,band_idx]]) for ir_idx in range(EDC_mtx.shape[0])]
            line_collections[band_idx] = LineCollection(band_EDC,
                                                        colors=band_color[band_idx],
                                                        linewidths=0.2,
                                                        label=label_list[band_idx],
                                                        zorder=6
                                                        )
        for col in line_collections:    
            ax.add_collection(col)

    @staticmethod
    def plot_Tn_data():
        pass

    @staticmethod
    def get_axis(ax):
        if ax is None:
            return plt.gca()
        else:
            return ax
