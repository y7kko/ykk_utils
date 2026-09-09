"""
Matplotlib utilities module

- Implements templates for plots (map, spectrogram)
- Implements useful macros for plot configurations (enable LaTex,set locale)
- Implements routines for use in illustrations(spine deletion, ticks deletion,)
"""
from .plot_map import plot_map
from .spectrogram import spectrogram
from .figgen import figgen
from .artmacros import delete_spines, delete_ticks, delete_all
from .config_macros import set_ptbr,enable_latex

# deprecated
from .config_macros import serif_font
