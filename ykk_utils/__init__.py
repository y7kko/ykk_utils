from .filterclass import OctFilter
from .edc import ykkEDC, EDCinstancer
from .DecompOps import DecompOps#, plot_map
from .ScannerTemplate import ScannerTemplate
from .RobotClass import RobotClass
from .FractionalBands import OctaveBands,ThirdOctaveBands
from .GlobalWorkspace import GlobalWorkspace
__all__ = ['OctFilter', 
           'ykkEDC', 
           'EDCinstancer', 
           'DecompOps', 
#           'plot_map',
           'ScannerTemplate',
           'RobotClass',
           'OctaveBands',
           'ThirdOctaveBands',
            'PlotRoutines',
            'GlobalWorkspace'
           ]

__version__ = '0.0.1'

__author__ = 'Bruno Miyata'
