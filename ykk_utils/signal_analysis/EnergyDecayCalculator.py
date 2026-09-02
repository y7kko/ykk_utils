"""
Classe dedicada a calcular a EDC de um sinal. 
"""
import numpy as np
import warnings
from ykk_utils.applications.DirectionalDecay import DEDCCalculator


class EnergyDecayCalculator(DEDCCalculator):
    def __init__(self,*args,**kwargs):
        warnings.warn("Classe depreciada e movida para ykk_utils.applications.DirectionalDecay.DEDCCalculator")
        super().__init__(*args,**kwargs)
