import matplotlib.pyplot as plt
import numpy as np
from ppro_meas_insitu import InsituMeasurementPostPro
from sequential_measurement import ScannerMeasurement
import os
from pathlib import Path


class MeasTools:
    def __init__(self,name:str,main_folder:str):
        """

        Args:
            name (str): Project name
            main_folder (str): Folder where project is
        """
        self.meas_obj = ScannerMeasurement(main_folder = main_folder, 
                              name = name,
                              start_new_measurement = False
                              )
        
        self.main_folder = main_folder
        self.name = name
        self.meas_obj.load()


    def rename(self, new_name:str):
        main_folder = self.main_folder
        name = self.name

        # Renomeia pickle
        pickle_file = Path(f'{main_folder}{name}/{name}.pkl')
        pickle_file.rename(f'{main_folder}{name}/{new_name}.pkl')

        # Renomeia folder
        project_folder = Path(main_folder + name)
        project_folder.rename(f'{main_folder}{new_name}')

        # Renomeia referências dentro da classe
        self.meas_obj.name = new_name
        self.meas_obj.main_folder = Path(main_folder)
        
        # Salva alterações
        self.meas_obj.save()
        self.name = new_name
