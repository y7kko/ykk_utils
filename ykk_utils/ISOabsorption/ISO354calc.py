#%%
import numpy as np
import matplotlib.pyplot as plt
# from .FractionalBands import OctaveBands,ThirdOctaveBands
from ..signal_analysis_utilities.edc_old import ykkEDC
# from .ISOcalc.ISO9613 import ISO9613 # Preferencia por AirProperties

from controlsair import AirProperties, AlgControls,cart2sph

#%%

class ISO354:
    def __init__(self,empty_room:ykkEDC,absorption_room:ykkEDC,
                 airprops_empty:AirProperties, airprops_abs:AirProperties,
                 room_volume,
                 area):
                
        self.empty_room = empty_room
        self.absorption_room = absorption_room
        
        self.freqs = empty_room.band_freqs
        self.airprops_empty = airprops_empty
        self.airprops_abs = airprops_abs

        self.c0 = {
            'empty' : self.airprops_empty.c0,
            'abs'   : self.airprops_abs.c0
        }

        self.air_abs = {
            'empty': self.airprops_empty.air_absorption(self.freqs),
            'abs': self.airprops_abs.air_absorption(self.freqs)

        }


        self.room_volume = room_volume
        self.area = area


    def calculate(self,kind='T20'):
        if kind == 'T20':
            RT = {
                'empty' : np.mean(self.empty_room.T20,axis=0),
                'abs'   : np.mean(self.absorption_room.T20,axis=0)
            }
        elif kind == 'T30':
            RT = {
                'empty' : np.mean(self.empty_room.T30,axis=0),
                'abs'   : np.mean(self.absorption_room.T30,axis=0)
            }
        
        condition = 'empty'
        self.A1 = self.An(Tn=RT[condition],
                          air_abs=self.air_abs[condition],
                          c0=self.c0[condition])
        
        condition = 'abs'
        self.A2 = self.An(Tn=RT[condition],
                          air_abs=self.air_abs[condition],
                          c0=self.c0[condition])

        self.AT = self.A2 - self.A1
        self.alpha_diffuse = self.AT/self.area
        return self.alpha_diffuse



    def An(self,Tn,c0,air_abs):
        V = self.room_volume
        m = air_abs/(10*np.log10(np.e))
        return (55.3*V/(c0*Tn)) - 4*V*m
    