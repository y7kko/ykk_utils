#%%
import numpy as np
import matplotlib.pyplot as plt
# from .FractionalBands import OctaveBands,ThirdOctaveBands
# from ..signal_analysis.edc_old import ykkEDC
# from .ISOcalc.ISO9613 import ISO9613 # Preferencia por AirProperties
from controlsair import AirProperties

#%%

class ISO354:
    def __init__(self,RT_empty,RT_abs,
                 airprops_empty:AirProperties, airprops_abs:AirProperties,
                 room_volume,
                 area,freq):

        for rt in [RT_empty,RT_abs]:
            if not len(rt) == len(freq):
                raise ValueError('length mismatch')

        self.RT_empty = RT_empty
        self.RT_abs = RT_abs
        
        self.freqs = freq
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


    def calculate(self):
        RT = dict(empty=self.RT_empty,abs=self.RT_abs)

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
    
    def plot_abs(self,ax=None):
        if ax is None:
            # if len(plt.gcf().axes) == 0:
            #     plt.figure()
            ax= plt.gca()
        artist = ax.plot(self.freqs,self.calculate())
        return artist
