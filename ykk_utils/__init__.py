from . import tools
from . import arraybackends

from .signal_analysis import dsputils, dsp_funcs
from .signal_analysis.FilterBank import FilterBank

from .file_management.GlobalWorkspace import GlobalWorkspace
from .file_management import colab_tools

from .signal_analysis.NominalFractionalBands import OctaveBands,ThirdOctaveBands
from .signal_analysis import error_funcs

from . import plot
from . import applications
from . import special_methods

# Alias para o modulo de plot
ykplot = plot

from .signal_analysis.EnergyDecayCalculator import EnergyDecayCalculator
__all__ = [
           'OctaveBands',
           'ThirdOctaveBands',
            'PlotRoutines',
            'GlobalWorkspace',
            'ykk_nmse',
            'ykk_nmse_freq',
            'PlottingLayouts',
            'error_funcs',
            'colab_tools',
            'plot',
            'ykplot',
            'FilterBank',
            'EnergyDecayCalculator',
            'dsputils',
            'dsp_funcs'
            'arraybackends',
            'tools',
            'applications',
            'special_methods',
           ]

__version__ = "1.9.0"

__author__ = 'Bruno Miyata'
