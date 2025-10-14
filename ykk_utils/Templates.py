#%% IMPORTS
import numpy as np
from sequential_measurement import ScannerMeasurement
from decompositionclass import Decomposition
from receivers import Receiver
from sources import Source
import pytta
import os
from typing import List


from datetime import datetime


#%%

class ScannerTemplate:
    """Classe funções utilitárias de medição com o ScannerMeasurement

    """
    source_template = Source(coord = [0, 0, 1])
    
    
    @staticmethod
    def instance_scanner(main_folder, name,
                        fft_degree, 
                        material_type,
                        microphone_type,
                        audio_interface,
                        amplifier,
                        start_stop_margin, 
                        temperature,                         #IMPORTANTE
                        humidity,
                        source,
                        fs = 44100,
                        mic_sens = 49.8,
                        pausing_time_array = [2,2,2], 
                        material = None, 
                        x_pwm_pin = 2, x_digital_pin = 24,y_pwm_pin = 3, y_digital_pin = 26, z_pwm_pin = 5, z_digital_pin = 28,dht_pin = 40,
                        source_type = 'spherical speaker', 
                        start_new_measurement = True
                        ):
        """Instância um objeto de medição pré configurado, útil para evitar redundância em casos de múltiplas medições

        Args:
            Consultar o ScannerMeasurement
        Returns:
            ScannerMeasurement: Um objeto de medição pré configurado
        """
        scanner_instance = ScannerMeasurement(main_folder = main_folder, 
                                name = name,
                                fft_degree = fft_degree, 
                                start_stop_margin = start_stop_margin, 
                                pausing_time_array = pausing_time_array, 
                                material_type = material_type,
                                microphone_type = microphone_type,
                                audio_interface = audio_interface,
                                amplifier = amplifier,
                                material = None, 
                                temperature = temperature,
                                humidity = humidity,
                                mic_sens = mic_sens,
                                x_pwm_pin = x_pwm_pin, x_digital_pin = x_digital_pin,
                                y_pwm_pin = y_pwm_pin, y_digital_pin = y_digital_pin, 
                                z_pwm_pin = z_pwm_pin, z_digital_pin = z_digital_pin,
                                dht_pin = dht_pin,
                                source_type = source_type, source = source,
                                fs = fs,
                                start_new_measurement = start_new_measurement
                                )
        scanner_instance.set_measurement_date()
        print("Sweep de " + str(round((2**scanner_instance.fft_degree)/(scanner_instance.fs))) + " s")
        return scanner_instance


    @staticmethod
    def get_metadata_dict() -> 'dict':
        """Retorna um dicionário template com apenas as variáveis obrigatórias de instance_scanner

        Returns:
            dict: Um dicionário com as váriaveis obrigatórias de instance_scanner()
        """
        meas_obj_dict = dict(main_folder='', 
                    name='',
                    fft_degree=0, 
                    material_type='',
                    microphone_type='',
                    audio_interface='',
                    amplifier='',
                    start_stop_margin=[], 
                    temperature=0,                         #IMPORTANTE
                    humidity=0,
                    source=ScannerTemplate.source_template,)
        return meas_obj_dict


    @staticmethod
    def configure_pytta(meas_objs: List['ScannerMeasurement'],device_number:int,**kwargs):
        """Configura o Pytta de múltiplos objetos de medição simultâneos

        Args:
            meas_objs (List[ScannerMeasurement]): Uma lista com os objetos de medição a serem configurados
            device_number (int): Número do dispositivo de gravação e reprodução
            **kwargs: Passado para o pytta_play_rec_setup()
        """
        if not isinstance(meas_objs,list):
            meas_objs = list(meas_objs)
        
        for meas_obj in meas_objs:
            meas_obj.pytta_set_device(device = device_number)
            meas_obj.pytta_play_rec_setup(**kwargs)


    @staticmethod
    def sweep_config(meas_objs: List['ScannerMeasurement'], **kwargs):
        """Configura o sinal matemático para multiplos objetos de medição

        Args:
            meas_objs (List[ScannerMeasurement]): Objetos de medição a serem configurados
        """
        if not isinstance(meas_objs,list):
            meas_objs = list(meas_objs)

        
        for meas_obj in meas_objs:
            meas_obj.set_meas_sweep(**kwargs)


    @staticmethod
    def move_back(meas_obj: ScannerMeasurement,invert_y=True,moveback=True,autoshutdown=True):
        """Calcula a distância do ultimo ponto até a origem e move o robô

        Args:
            meas_obj (ScannerMeasurement): A classe de medição ativa
            invert_y (bool, optional): Inverter o eixo y(util por conta da convenção do stand_array). Defaults to True.
        """
        
        final_point = meas_obj.receivers.coord[-1].copy()
        if invert_y:
            final_point[1] *= -1
        moveback_dist = meas_obj.pt0 - final_point
        if moveback:
            meas_obj.move_motor_xyz(moveback_dist)
        if autoshutdown:
            meas_obj.board.shutdown()
        


    @staticmethod
    def auto_name(material:str,L:str,d:str,meas_type:str,date=None,unit='cm') -> 'str':
        """Gera um nome na convenção proposta do projeto

        Args:
            material (str): O nome do material medido
            L (str): Dimensoes do material
            d (str): Espessura do material
            meas_type (str): Tipo de medição
            date (str, optional): Usar formato ddmmaa. Defaults to today.
            unit (str, optional): Unidade de medida de 'L' e 'd'. Defaults to 'cm'.

        Returns:
            str: Um nome nas convenções propostas pelo Eric
        """
        if date is None:
            date = datetime.now().strftime('%d%m%Y')
        name = f"{material}_L{L}{unit}_d{d}{unit}_{meas_type}_{date}"
        return name


class DecompMacros:
    @staticmethod
    def load_checkpoint(main_folder,
                        name,
                        checkpoint_name='decomp_checkpoint'):
        projpath = main_folder + name + '/'
        decomp_obj = Decomposition() # instancia vazio para overwrite
        decomp_obj.load(filename = checkpoint_name, 
                        path = str(projpath))
        return decomp_obj
    
    @staticmethod
    def save_checkpoint(main_folder,
                        name,
                        decomp_obj:Decomposition,
                        checkpoint_name='decomp_checkpoint',
                        ):
        projpath = main_folder + name + '/'
        os.makedirs(projpath,exist_ok=True)
        decomp_obj.save(filename = checkpoint_name, 
                        path = str(projpath))

