import matplotlib.pyplot as plt
import numpy as np

def delete_all(ax:plt.Axes=None):
    delete_ticks(ax)
    delete_spines(ax)


def delete_spines(ax:plt.Axes=None):
    if ax is None:
        ax = plt.gca()
    
    if ax.name == '3d':
        _3d_spine_del(ax)
    else:
        print('lembrar de remover spines')
    pass

def delete_ticks(ax:plt.Axes=None):
    if ax is None:
        ax = plt.gca()

    ax.set_xticks([])
    ax.set_yticks([])
    if ax.name == '3d':
        ax.set_zticks([])  # [citation:2]



#chatgptado
def _3d_spine_del(ax:plt.Axes):
    """Apaga o fundo de plots com projection 3d """
    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
        axis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        axis.line.set_color((1.0, 1.0, 1.0, 0.0))
        axis._axinfo["grid"]['color'] = (1,1,1,0)
