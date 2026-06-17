import matplotlib.pyplot as plt
from controlsair import cart2sph
import matplotlib.patheffects as PathEffects
import numpy as np

def plot_map(dir:np.ndarray, p:np.ndarray, 
             ax:plt.Axes = None,whitexticks=True, **kwargs):
        """Realiza o plot do mapa de decomposição em ondas planas

        Args:
            dir (np.ndarray): Vetor de direções de cada onda plana dir1 = [(x,y,z)] 
            p (np.ndarray): Pressão em cada direção p(x,y,z)
            dinrange (int, optional): Alcance dinâmico do plot. Defaults to 20.
            return_current (bool, optional): Retornar ax e fig. Defaults to True.

        Returns:
            _type_: ax e pc
        """
        if ax is None:
            ax = plt.axes(projection='hammer')
        elif ax.name != 'hammer':
             raise ValueError("axis não utiliza projeção 'hammer'.")
            

        defaults = dict(cmap='inferno',shading='gouraud')
        kwargs = {**defaults,**kwargs}
        
        _, elv, azm = cart2sph(dir[:,0],dir[:,1],dir[:,2]) 

        tc = ax.tripcolor(azm, elv, p, zorder=1,**kwargs)
        ax.grid(True,zorder=2,alpha=0.5)

        if whitexticks:        
            for label in ax.get_xticklabels():
                label.set_color('white')
                label.set_path_effects([
                    PathEffects.withStroke(linewidth=2, foreground='#00000077')
                ])
                label.set_zorder(90)
                
        return tc
