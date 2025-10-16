import numpy as np
from sequential_measurement import ScannerMeasurement
from receivers import Receiver
from sources import Source
import pytta
import os
import matplotlib.pyplot as plt

class ArrayInspector:
    def __init__(self, meas_obj:ScannerMeasurement):
        self.meas = meas_obj
        self.axis = dict(x=0,y=1,z=2)
        self.coord = meas_obj.receivers.coord
        self.stand = meas_obj.stand_array

    def plot_maximum_movement(self,axis='x',show_maximum=True):
        axis_idx = self.axis[axis]
        stand_array = self.meas.stand_array[:,axis_idx]
        
        
        plt.figure()
        plt.plot(stand_array)
 
        if show_maximum:
            argmax = np.abs(stand_array.argmax())
            plt.scatter(argmax, stand_array[argmax, axis_idx])
            plt.annotate(f'dx = {stand_array[argmax,axis_idx]:.2f} m', 
                        (argmax, stand_array[argmax,axis_idx]))

        plt.title(self.meas.name)
        plt.grid()

    def plot_coords_error(self,axis='x',compare_with_stand=True,invert_y=True):
        ax_idx  = self.axis[axis]
        stand_array = self.meas.stand_array[:,ax_idx]
        coords  = self.meas.receivers.coord[:,ax_idx]

        accum_stand = stand_array.cumsum()
        if invert_y and ax_idx==1:
            accum_stand *= -1
        
        # plt.figure()
        plt.plot(coords)
        plt.plot(accum_stand)

    def plot_plane(self,axis1='x',axis2='y',show_indices=True):
        axis1 = self.axis[axis1]
        axis2 = self.axis[axis2]


        plt.plot(self.coord[:,0],self.coord[:,1],linewidth=0.7)
        plt.scatter(self.coord[:,0],self.coord[:,1],s=15)
        plt.scatter(self.coord[0,0],self.coord[0,1],c='green')
        plt.scatter(self.coord[-1,0],self.coord[-1,1],c='red')

        if show_indices:
            for idx,x,y in zip(np.arange(len(self.coord[:,1])), self.coord[:,0],self.coord[:,1]):
                plt.annotate(f'{idx}',[x,y])

    def plot_coords_error(self,axis='x',compare_with_stand=True,invert_y=True):
        ax_idx  = self.axis[axis]
        stand_array = self.meas.stand_array[:,ax_idx]
        coords  = self.meas.receivers.coord[:,ax_idx]

        accum_stand = stand_array.cumsum()
        if invert_y and ax_idx==1:
            accum_stand *= -1
        
        plt.plot(coords-accum_stand)


    def __repr__(self):
        stand = self.meas.stand_array
        maxstand = list(
            stand[np.abs(stand[:,idx]).argmax(),idx] for idx in range(3)
            )

        txt = f"""
:::Measurement: {self.meas.name}

- max(stand): [{maxstand[0]:.3f}, {maxstand[1]:.3f}, {maxstand[2]:.3f}]

"""
        return txt    
