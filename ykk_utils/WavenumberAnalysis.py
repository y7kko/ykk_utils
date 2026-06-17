import matplotlib.pyplot as plt
import numpy as np
from controlsair import AirProperties, AlgControls,cart2sph
from decompositionclass import Decomposition
from .signal_analysis.NominalFractionalBands import ThirdOctaveBands,OctaveBands
import matplotlib.patheffects as PathEffects

class WavenumberAnalysis:
    """Classe para analisar o espectro do número de onda de uma decomposição em ondas planas

    Método: A wavenumber approach to quatifying piririr pororo (Nolan, 2020)
    """
    def __init__(self, pk,dir,freq, travel=True, ymirror=False):
        """Classe utilizada para realizar operações com a decomposição em ondas planas

        Args:
            pk (ndarray): coeficiente complexos do espectro de  número de onda
            dir (ndarray): Coordenadas de cada onda plana
            freq (ndarray): Frequências para qual o campo foi desconstruido
            travel (bool, optional): _description_. Defaults to True.
            ymirror (bool, optional): _description_. Defaults to False.
        """
        self.dir = dir
        self.travel = travel
        if self.travel:
            self.dir[:,2] *= -1
        if ymirror:
            self.dir[:,1] *= -1

        self.pk = pk
        self.freq = freq

    def from_decomposition(self, decomp_obj:Decomposition,**kwargs):
        """Inicializa a classse utilizando uma instância do insitu_sim

        Args:
            decomp_obj (Decomposition): Classe que contém os dados de decomposição 

        Returns:
            self
        """
        self.__init__(dir=decomp_obj.dir, 
                      pk = decomp_obj.pk,
                      freq=decomp_obj.controls.freq,
                      **kwargs
                      )
        return self

    def change_travel(self,travel: bool):
        """Alterna entre direção de propagação e direção de chegada

        Args:
            travel (bool): Caso True a direção é a direção de propagação, 
            caso False a direção é a direção de chegada
        """
        if travel != self.travel:
            self.travel =  not self.travel
            self.dir[:,2] *= -1


    def plot_map(self, 
                 dinrange=20,freq=1000,kind='oct',decibel=True,
                 fig=None,colorbar=True,projection='hammer',ax=None,title=True,return_something=False,**kwargs):
        """Realiza o plot do mapa em projeção cartográfica (Hammer)

        Args:
            dinrange (int, optional): O mínimo valor em dB a ser apresentado. Defaults to -20.
            freq (int, optional): A frequência de referência. Defaults to 1000.
            kind (str, optional): Como será analisado a frequência.
                                    Use 'oct' para banda de oitava.
                                    'third' para terço de oitava,
                                    'single' para a frequencia unica.
                                    Defaults to 'oct'.
        """
        freq_idx, freq = self._get_freq_idx(freq, kind)
        
        if fig is None:
            fig = plt.gcf()
        if ax is None:
            ax = plt.axes(projection = projection)

        pk = self._pk_mean(freq_idx)
        pk = abs(pk)/ max(abs(pk))
        if decibel:
            pk = 20*np.log10(pk)

        dir = self.dir
        
        pc = PlotRoutines.plot_map(
                        dir = dir,
                        p = pk,
                        ax=ax,**kwargs
                        )

        if decibel:
            pc.set_clim([-dinrange, 0])
            colorbar_label = "Magnitude (dB)"
        else:
            if dinrange > 1:
                Warning('dinrange está alto para p(k) linear')
            pc.set_clim([0,dinrange])
            colorbar_label = "Magnitude (-)"

        
        if colorbar:
            cbar = fig.colorbar(pc, orientation="horizontal", label=colorbar_label)


        if title:
            plt.title(f"|P(k)| - {freq:.2f} Hz - kind: {kind} - Travel: {self.travel}",pad=20)
        if return_something:
            return pc

    
        
    def plot_sphere(self, dinrange=20, freq=1000, kind='oct',
                    ax=None,fig=None, az=-60,elev=30,decibel=True,title=True):
        freq_idx, freq = self._get_freq_idx(freq, kind)
        
        pk = self._pk_mean(freq_idx)
        pk = abs(pk)/ max(abs(pk))
        if fig is None:
            fig = plt.gcf()
        if ax is None:
            ax = plt.axes(projection='3d')
       
        if decibel:
            pk = 20*np.log10( pk)
            vminmax = [-dinrange,0]
            colorbar_label = "Magnitude (dB)"

        else:
            vminmax = [0,dinrange]
            colorbar_label = "Magnitude (-)"


        scatter = PlotRoutines.plot_sphere(
                        dir=self.dir, 
                        p=pk, 
                        ax=ax,
                        vminmax=vminmax
                        )



        cbar = fig.colorbar(scatter,label=colorbar_label)

        ax.set_xlabel(r'$k_x$')
        ax.set_ylabel(r'$k_y$')
        ax.set_zlabel(r'$k_z$')
        ax.view_init(azim=az,elev=elev)



        plt.title(f'|P(k)| - {freq:.2f} Hz - kind: {kind} - Travel: {self.travel}',pad=20)
    
    def estimate_abs_naive(self,):
        # variable initialization
        pk = self.pk 
        pk = np.abs(pk**2)
        direction = self.dir 
        n_dir = len(direction[:,0]) #número de ondas planas
        
        
        #coord trasnform
        if not self.travel: #forces to be travelling direction
            direction[:,2]  *= -1
        
        _, elv, azm = cart2sph(direction[:,0],direction[:,1],direction[:,2]) 

        unique_elv = np.unique(elv)
        pk_theta = np.zeros(unique_elv.shape)
        alpha_theta = np.zeros(int(np.ceil(unique_elv.shape[0]/2)))
        alpha_freq = np.zeros(pk.shape[1])

        for freq_idx in range(pk.shape[1]):
            for unique_idx in range(unique_elv.shape[0]):
                idx = np.where(elv == unique_elv[unique_idx])[0]
                pk_theta[unique_idx] = np.sum(pk[idx,freq_idx])
            

            for theta_idx in range(len(alpha_theta)):
                alpha_theta[theta_idx] = 1 - pk_theta[theta_idx]/pk_theta[-theta_idx]

            elv_idx = int(np.ceil(unique_elv.shape[0]/2))
            alpha_diff = 2*np.sum(alpha_theta*np.cos(unique_elv[elv_idx])*np.sin(unique_elv[elv_idx]))
            alpha_freq[freq_idx] = alpha_diff
        return alpha_freq
        # return alpha_theta
        

    # Rever se to fazendo media do jeito certo
    #talvez utilizar squeeze
    def _pk_mean(self, freq_index):
        """Calcula a magnitude média de cada direção de propagação.
        Caso freq_index seja composto de um único valor a média é o próprio modulo
        dos pontos na frequência especifica

        Args:
            freq_index (np.ndarray, int): As frequências que entram na média

        Returns:
            np.ndarray: A magnitude média de cada direção de propagação
        """
        if np.size(freq_index)>1:
            pk = np.mean(np.abs(self.pk[:,freq_index]), axis=1)
        else:
            pk = np.abs(self.pk[:,freq_index])
        return pk
    

    
    def _get_freq_idx(self,freq,kind):
        """Obtem os índices de frequência para uma banda ou frequência individual

        Args:
            freq (float): Frequência central ou frequência esperada
            kind (str): 
                caso 'oct': Utilizar limites de banda de oitava
                caso 'third': Utilizar limites de banda de terço de oitava
                caso 'single': Obter frequência mais proxima

        Returns:
            np.ndarray, int: Os indices das frequências pertencentes à banda de analise
            np.ndarray, float: A frequência nominal da banda. Caso 'single' a frequência
            nominal será a frequência no índice
        """
        if kind == 'oct':
            band_class = OctaveBands

        elif kind == 'third':
            band_class = ThirdOctaveBands        
        
        elif kind == 'single': #Early return
            freq_idx = np.argmin(np.abs(self.freq-freq))
            return freq_idx, self.freq[freq_idx]

        center_freqs = band_class.center_freqs()
        minmax_freqs = band_class.minmax_freqs()

        # indice da frequência central mais proxima de freq
        freq_idx = np.argmin(np.abs(center_freqs-freq))
        
        # Todos os indices com frequencia contidas na banda de freq_idx
        minmax_idx = np.where(
            (self.freq >= minmax_freqs[freq_idx][0]) & 
            (self.freq <= minmax_freqs[freq_idx][1]) )[0]
        
        return minmax_idx, center_freqs[freq_idx]






class PlotRoutines:
    """Rotinas de plot

    """
    @staticmethod
    def plot_map(dir,p,
                 ax=None,**kwargs):
        """Realiza o plot do mapa de decomposição em ondas planas

        Args:
            dir (np.ndarray): Vetor de direções de cada onda plana dir1 = [(x,y,z)] 
            p (np.ndarray): Pressão em cada direção p(x,y,z)
            dinrange (int, optional): Alcance dinâmico do plot. Defaults to 20.
            return_current (bool, optional): Retornar ax e fig. Defaults to True.

        Returns:
            _type_: ax e pc
        """
        defaults = dict(cmap='inferno',shading='gouraud')
        kwargs = {**defaults,**kwargs}
        _, elv, azm = cart2sph(dir[:,0],dir[:,1],dir[:,2]) 


        tripcolor = ax.tripcolor(azm, elv, p, zorder=1,**kwargs)
        ax.grid(True,zorder=2,alpha=0.5)

        
        for label in ax.get_xticklabels():
            label.set_color('white')
            label.set_path_effects([
                PathEffects.withStroke(linewidth=2, foreground='#00000077')
            ])
            label.set_zorder(90)

        return tripcolor


    @staticmethod
    def plot_sphere(dir, p, ax, vminmax:list):
        """Realiza o plot da esfera de decomposição em ondas planas

        Args:
            dir (np.ndarray): Vetor de direções de cada onda plana dir1 = [(x,y,z)] 
            p (np.ndarray): Pressão em cada direção p(x,y,z)
            dinrange (int, optional): Alcance dinâmico do plot. Defaults to 20.
            az (int, optional): Azimute da perspectiva. Defaults to -60.
            elev (int, optional): Elevação da perspectiva. Defaults to 30.
            return_current (bool, optional): Retornar ax e fig. Defaults to True.

        Returns:
            _type_: ax e fig
        """
        scatter = ax.scatter(dir[:,0], dir[:,1], dir[:,2], c = p,
                           vmin = vminmax[0], vmax = vminmax[1],cmap="inferno",s=50)
        
        return scatter
        