import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from decompositionclass import Decomposition
from ppro_meas_insitu import InsituMeasurementPostPro
from controlsair import AirProperties, AlgControls#, add_noise, add_noise2
from .signal_analysis.error_funcs import Efren
from .signal_analysis.NominalFractionalBands import OctaveBands,ThirdOctaveBands

class ReconstructionAnalyser:
    """Classe para comparar erros de reconstrução do meu TCC1.
    """
    def __init__(self,decomp_obj:Decomposition,rec_ppro:InsituMeasurementPostPro,decomp_ppro:InsituMeasurementPostPro):
        self.decomp_obj = decomp_obj
        self.rec_ppro = rec_ppro
        self.freq = decomp_obj.controls.freq
        self.rec_receivers = rec_ppro.meas_obj.receivers

        if not hasattr(self.decomp_obj,'p_recon'):
            self.decomp_obj.reconstruct_pu(self.rec_receivers)
        
        self.decomp_receivers = decomp_ppro.meas_obj.receivers


        self.n_pts = rec_ppro.meas_obj.receivers.coord.shape[0]
        self.freq_min = rec_ppro.freq_Hw[0]
        self.freq_max = rec_ppro.freq_Hw[-1]


    def mean_freq_error(self,):
        p_decomp = self.decomp_obj.p_recon
        p_record = self.rec_ppro.Hww_mtx

        self.epsilon = Efren.freq_error(p_decomp,p_record)
        

    def plot_freq_recording(self,rec_idx:int, db=True,use_lowres=True,ax=None,**kwargs):
        if use_lowres:
            p = self.rec_ppro.Hww_mtx[rec_idx,:]
            freq = self.rec_ppro.freq_Hw
        else:        
            p = self.rec_ppro.Hw_mtx[rec_idx,:]
            # Como o vetor frequência é discretizado inplace, tem que refazer por fora
            freq = LocalUtils.new_freq_vec(n_spl = self.rec_ppro.ht_mtx.shape[1],
                                           fs    = self.rec_ppro.meas_obj.fs)

        if db:
            p = 20*np.log10(np.abs(p))
        else:
            p = np.abs(p)

        ax = LocalUtils.select_axis(ax)

        ax.plot(freq,p,**kwargs)

    def plot_freq_decomp(self,rec_idx:int, db=True,ax=None,**kwargs):            
        p = self.decomp_obj.p_recon[rec_idx,:]
        freq = self.freq

        if db:
            p = 20*np.log10(np.abs(p))
        else:
            p = np.abs(p)

        ax = LocalUtils.select_axis(ax)

        ax.plot(freq,p,**kwargs)


    def plot_freq_error(self,rec_idx:int,ax=None,**kwargs):
        ax = LocalUtils.select_axis(ax)
        freq = self.freq

        p_decomp = self.decomp_obj.p_recon[rec_idx,:]
        p_record = self.rec_ppro.Hww_mtx[rec_idx,:]

        epsilon = Efren.freq_error(p_decomp,p_record)

        ax.plot(freq,epsilon,**kwargs)


    def plot_mean_freq_error(self,ax=None,third=False,**kwargs):
        ax = LocalUtils.select_axis(ax)
        freq = self.freq

        p_decomp = self.decomp_obj.p_recon
        p_record = self.rec_ppro.Hww_mtx

        epsilon = Efren.freq_error(p_decomp,p_record)
        self.epsilon_freq = epsilon

        if third:
            indexes2plot = LocalUtils.third_indexes(freq)
            freq = freq[indexes2plot]
            epsilon = np.zeros(len(freq))
            for third_idx,f in enumerate(freq):
                _,flims = ThirdOctaveBands.get_band(f)
                f_idx = np.where((self.freq >= flims[0]) & (self.freq<=flims[1]))[0]
                epsilon[third_idx] = np.mean(self.epsilon_freq[f_idx])
            # epsilon, freq = self.third_octave_epsilon()



        ax.plot(freq,epsilon,**kwargs)

    def compute_epsilon(self):
        indexes2plot = LocalUtils.third_indexes(self.freq)
        # print(indexes2plot)
        freq = self.freq[indexes2plot]
        epsilon = np.zeros(len(freq))
        for third_idx,f in enumerate(freq):
            _,flims = ThirdOctaveBands.get_band(f)
            f_idx = np.where((self.freq >= flims[0]) & (self.freq<=flims[1]))[0]
            epsilon[third_idx] = np.mean(self.epsilon_freq[f_idx])
        return epsilon, freq

    def plot_std_freq_error(self,ax=None,**kwargs):
        Warning('Não implementei')
        pass

    def plot_spatial_error(self,freq,show_array_lims=False,ax=None,use_scatter=False,**kwargs):
        ax = LocalUtils.select_axis(ax)

        p_decomp = self.decomp_obj.p_recon
        p_record = self.rec_ppro.Hww_mtx


        freq_idx = np.abs(self.freq - freq).argmin()
        pos_error = np.zeros(self.n_pts)
        for rec_idx in range(self.n_pts):
            error = Efren.spatial_epsilon(p_decomp[rec_idx,freq_idx],p_record[rec_idx,freq_idx])            
            pos_error[rec_idx] = 20*np.log10(error)

        point_coord = self.rec_receivers.coord 
        point_coord = point_coord[:,:2] #xy

        if use_scatter:
            artist = LocalUtils.scatter2d(point_coord,pos_error,ax=ax,**kwargs)
        else:
            artist = LocalUtils.colormesh2d(point_coord,pos_error,ax=ax,**kwargs)
        

        if show_array_lims:
            self._plot_array_lims(ax)
        return artist
    
    def plot_spatial_pressure(self,freq,reconstruction=True,show_array_lims=False,ax=None,use_scatter=False,**kwargs):
        ax = LocalUtils.select_axis(ax)

        p_decomp = self.decomp_obj.p_recon
        p_record = self.rec_ppro.Hww_mtx


        freq_idx = np.abs(self.freq - freq).argmin()
        # pos_error = np.zeros(self.n_pts)
        # for rec_idx in range(self.n_pts):
        #     error = Efren.spatial_epsilon(p_decomp[rec_idx,freq_idx],p_record[rec_idx,freq_idx])            
        #     pos_error[rec_idx] = 20*np.log10(error)

        point_coord = self.rec_receivers.coord 
        point_coord = point_coord[:,:2] #xy

        if reconstruction:
            pos_pressure = p_decomp[:,freq_idx]
        else:
            pos_pressure = p_record[:,freq_idx]
        # pos_pressure
        pos_pressure= 20*np.log10(np.abs(pos_pressure))
        if use_scatter:
            artist = LocalUtils.scatter2d(point_coord,pos_pressure,ax=ax,**kwargs)
        else:
            artist = LocalUtils.colormesh2d(point_coord,pos_pressure,ax=ax,**kwargs)
        

        if show_array_lims:
            self._plot_array_lims(ax)
        return artist
    

    
    def _plot_array_lims(self,ax=None):
        ax = LocalUtils.select_axis(ax)
        array_coord = self.decomp_receivers.coord[:,:2]
        ax.add_patch(Rectangle((min(array_coord[:,0]),
                                min(array_coord[:,1])
                                ),
                                width=max(array_coord[:,0]) - min(array_coord[:,0]),
                                height=max(array_coord[:,1]) - min(array_coord[:,1]),
                                zorder=1,
                                hatch='xx',
                                fill=False,
                                linewidth=0,
                                alpha=0.2
                                )
                    )








class LocalUtils:
    @staticmethod
    def select_axis(ax=None):
        if ax is None:
            return plt.gca()
        else:
            return ax
    
    @staticmethod
    def new_freq_vec(n_spl,fs):
        if (n_spl % 2) == 0:
                nfft_half = int(n_spl/2)
        else:
            nfft_half = int((n_spl+1)/2)
        return np.linspace(0, (n_spl-1)*fs/n_spl, n_spl)[:nfft_half]
    
    def scatter2d(points,color,ax,**kwargs):
        
        defaults = dict(
                        edgecolor='k', 
                        s=150,
                        alpha=1,
                        cmap='inferno',
                        zorder=7
                        )
        kwargs = {**defaults,**kwargs}
        
        scatter = ax.scatter(points[:,0], 
                      points[:,1], 
                      c=color,**kwargs)  # pontos medidos
        return scatter

    def colormesh2d(coord,p,ax,**kwargs):
        
        defaults=dict(
                    shading='auto', 
                    cmap='inferno'
                    )
        kwargs = {**defaults,**kwargs}


        # Extrair coordenadas únicas
        x_unique = np.unique(coord[:, 0])
        y_unique = np.unique(coord[:, 1])

        # Criar grid 2D
        X, Y = np.meshgrid(x_unique, y_unique)

        # Reorganizar os valores p no formato do grid
        P_grid = np.zeros_like(X)

        # Preencher o grid com os valores de p
        for i, (x, y) in enumerate(coord):
            # Encontrar índices no grid
            idx_x = np.where(x_unique == x)[0][0]
            idx_y = np.where(y_unique == y)[0][0]
            P_grid[idx_y, idx_x] = p[i]  # Note: pcolormesh usa [linha, coluna]


        heatmap = ax.pcolormesh(X, Y, P_grid, **kwargs)
        return heatmap

    def third_indexes(freq:np.ndarray):
        """Retorna os índices do vetor de frequências mais próximo ao da banda de terço de oitava

        Args:
            freq (np.ndarray): _description_

        Returns:
            _type_: _description_
        """
        center = ThirdOctaveBands.center_freqs([freq.min(),freq.max()])
        indexes = np.zeros(len(center))
        for third_idx in range(len(indexes)):
            idx =  np.abs(freq-center[third_idx]).argmin()
            indexes[third_idx] = idx
        return indexes.astype(int)
