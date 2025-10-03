import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from controlsair import AirProperties, AlgControls,cart2sph
from decompositionclass import Decomposition
from .FractionalBands import ThirdOctaveBands,OctaveBands
import matplotlib.patheffects as PathEffects

class DecompOps:
    def __init__(self, decomp_obj:Decomposition, travel=True, ymirror=False):
        """Classe utilizada para realizar operações com a decomposição em ondas planas

        Args:
            decomp_obj (decompositionclass.Decomposition): O objeto de decomposição com ondas planas já calculadas
        """
        self.dir = decomp_obj.dir
        self.travel = travel
        if self.travel:
            self.dir[:,2] *= -1
        if ymirror:
            self.dir[:,1] *= -1

        self.pk = decomp_obj.pk
        self.freq = decomp_obj.controls.freq

    def change_travel(self,travel: bool):
        """Alterna entre direção de propagação e direção de chegada

        Args:
            travel (bool): Caso True a direção é a direção de propagação, 
            caso False a direção é a direção de chegada
        """
        if travel != self.travel:
            self.travel =  not self.travel
            self.dir[:,2] *= -1

    def plot_map(self, dinrange=20,freq=1000,kind='oct',decibel=True,**kwargs):
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

        pk = self._pk_mean(freq_idx)
        pk = abs(pk)/ max(abs(pk))
        if decibel:
            pk = 20*np.log10(pk)
        # pk = self._pk_calc(freq,kind)
        dir = self.dir
        
        plt_refs = PlotRoutines.plot_map(
                        dir = dir,
                        p = pk,
                        dinrange = dinrange,
                        projection="hammer",
                        return_current=True,
                        **kwargs
                        )
        
        plt.title(f"|P(k)| - {freq:.2f} Hz - kind: {kind} - Travel: {self.travel}",pad=20)
        return plt_refs

        
    def plot_sphere(self, dinrange=20, freq=1000, kind='oct', az=-60,elev=30,decibel=True,**kwargs):
            freq_idx, freq = self._get_freq_idx(freq, kind)
            
            pk = self._pk_mean(freq_idx)
            pk =abs(pk)/ max(abs(pk))
            if decibel:
                pk = 20*np.log10( pk)

            plt_refs = PlotRoutines.plot_sphere(
                            dir=self.dir, 
                            p=pk, 
                            dinrange=dinrange, 
                            az=az,
                            elev=elev,
                            return_current=True,
                            **kwargs)
            
            plt.title(f'|P(k)| - {freq:.2f} Hz - kind: {kind} - Travel: {self.travel}',pad=20)
            return plt_refs
    

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
    def plot_map(dir,p,dinrange=20,
                 projection='hammer',
                 return_current=True,
                 ax=None,
                 fig=None,colorbar=True):
        """Realiza o plot do mapa de decomposição em ondas planas

        Args:
            dir (np.ndarray): Vetor de direções de cada onda plana dir1 = [(x,y,z)] 
            p (np.ndarray): Pressão em cada direção p(x,y,z)
            dinrange (int, optional): Alcance dinâmico do plot. Defaults to 20.
            return_current (bool, optional): Retornar ax e fig. Defaults to True.

        Returns:
            _type_: ax e fig
        """
        return_list = []
        _, elv, azm = cart2sph(dir[:,0],dir[:,1],dir[:,2]) 
        # lon = np.degrees(azm)
        # lat = np.degrees(elv)
        if fig is None:
            fig = plt.gcf()
        fig.set_layout_engine('tight')

        if ax is None:
            ax = plt.axes(projection = projection)
            return_list.append(ax)
            # ax = fig.add_subplot(projection ="hammer")
    
        pc = ax.tripcolor(azm, elv, p, cmap="inferno",shading='gouraud')
        pc.set_clim([-dinrange, 0])
        ax.grid(True)


        if colorbar:
            cbar = fig.colorbar(pc, orientation="horizontal", label="Magnitude (dB)")
            return_list.append(cbar)
        
        for label in ax.get_xticklabels():
            label.set_color('white')
            label.set_path_effects([
                PathEffects.withStroke(linewidth=2, foreground='#00000077')
            ])

        if return_current:
            return return_list


    def plot_sphere(dir,p, dinrange=20, az=-60,elev=30,return_current=True,ax=None,fig=None):
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
        if fig is None:
            fig = plt.gcf()
        fig.set_layout_engine('tight')

        # ax = fig.add_subplot(projection ="3d")
        if ax is None:
            ax = plt.axes(projection ="3d")


        p=ax.scatter(dir[:,0], dir[:,1], dir[:,2], c = p,
                        vmin = -dinrange, vmax = 0,cmap="inferno",s=50)
        
        cbar = fig.colorbar(p,label="Magnitude (dB)")
        ax.set_xlabel(r'$k_x$ axis')
        ax.set_ylabel(r'$k_y$ axis')
        ax.set_zlabel(r'$k_z$ axis')
        ax.view_init(azim=az,elev=elev)
        if return_current:
            return ax,cbar
