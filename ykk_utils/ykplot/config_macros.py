import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import locale

def serif_font():
    """Muda o sistema global de fontes do matplotlib para
    LaTeX + Times New Roman
    """
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
    })


def set_ptbr():
    locale.setlocale(locale.LC_NUMERIC, 'pt_BR.UTF-8')
    plt.rcParams['axes.formatter.use_locale'] = True
