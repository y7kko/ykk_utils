import numpy as np
import os

_oct_center_freqs = np.array([16, 31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000])
_oct_minmax_freqs = np.array([[11.0, 22.1],
                              [22.1, 44.2],
                              [44.2, 88.4],
                              [88.4, 176.8],
                              [176.8, 353.6],
                              [353.6, 707.1],
                              [707.1, 1414.2],
                              [1412.2, 2828.4],
                              [2828.4, 5656.9],
                              [5656.9, 11313.7],
                              [11313.7, 22627.4]]
)
_thrd_center_freqs = np.array([16, 20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000,])
_thrd_minmax_freqs = np.array([
                                [13.9, 17.5],
                                [17.5, 22.1],
                                [22.1, 27.8],
                                [27.8, 35.1],
                                [35.1, 44.2],
                                [44.2, 55.7],
                                [55.7, 70.2],
                                [70.2, 88.4],
                                [88.4, 111.4],
                                [111.4, 140.3],
                                [140.3, 176.8],
                                [176.8, 222.7],
                                [222.7, 280.6],
                                [280.6, 353.6],
                                [356.6, 445.4],
                                [445.4, 561.2],
                                [561.2, 707.1],
                                [707.1, 890.9],
                                [890.9, 1122.5],
                                [1122.5, 1414.2],
                                [1414.2, 1781.8],
                                [1781.8, 2244.9],
                                [2244.9, 2828.4],
                                [2828.4, 3563.6],
                                [3563.6, 4489.8],
                                [4489.8, 5656.9],
                                [5656.9, 7127.2],
                                [7127.2, 8979.7],
                                [8979.7, 11313.7],
                                [11313.7, 14254.4],
                                [14254.4, 17959.4],
                                [17959.4, 22627.4]])
    
class OctaveBands:
    @staticmethod
    def center_freqs(freq_lims=[None,None]): #Faz caching a nivel de modulo
        """Retorna as frequências mínimas e máximas que correspondem a cada banda de terço de oitava 
        no intervalo especificado.

        Args:
            freq_lims (list, optional): frequências mínimas e máximas (intervalo fechado). Defaults to [None,None].

        Returns:
            np.ndarray: Array [n_bands, 2] contendo os limites da banda
        """

        global _oct_center_freqs
            
        if freq_lims[0] is None:
            freq_lims[0] = 0
        if freq_lims[1] is None:
            freq_lims[1] = _oct_center_freqs[-1]

        idx_lim = np.where((_oct_center_freqs >= freq_lims[0]) & 
                                (_oct_center_freqs <= freq_lims[1])
                                )[0]
        return _oct_center_freqs[idx_lim]

    @staticmethod
    def minmax_freqs(freq_lims=[None,None]): #Faz caching a nivel de modulo
        """Retorna as frequências mínimas e máximas que correspondem a cada banda de terço de oitava 
        no intervalo especificado.

        Args:
            freq_lims (list, optional): frequências mínimas e máximas (intervalo fechado). Defaults to [None,None].

        Returns:
            np.ndarray: Array [n_bands, 2] contendo os limites da banda
        """

        global _oct_minmax_freqs
        global _oct_center_freqs
        idx_lim = np.where((_oct_center_freqs >= freq_lims[0]) & 
                        (_oct_center_freqs <= freq_lims[1])
                        )[0]

        return _oct_minmax_freqs[idx_lim]
    
    @staticmethod
    def get_band(freq=1000):
        """[QUEBRADO] Busca a banda da frequência especificada e retorna a frequência central,
        bem como os limites.

        * Fazer com que cheque a qual banda a frequência pertence. Ao invés de buscar a banda mais próxima

                Args:
            freq (int, optional): _description_. Defaults to 1000.

        Returns:
            _type_: _description_
        """

        center_freqs = OctaveBands.center_freqs()
        minmax_freqs = OctaveBands.minmax_freqs()
        idx = (abs(center_freqs-freq)).argmin()
        return center_freqs[idx], minmax_freqs[idx]



class ThirdOctaveBands:
    @staticmethod
    def center_freqs(freq_lims=[None,None]) -> 'np.ndarray':
        """Retorna as frequências centrais de cada banda de terço de oitava no intervalo especificado. 

        Args:
            freq_lims (list, optional): Banda mínima e máxima (intervalo fechado). Defaults to [None,None].

        Returns:
            np.ndarray: Um array com as frequências centrais de cada banda. 
        """
        global _thrd_center_freqs

        
        if freq_lims[0] is None:
            freq_lims[0] = 0
        if freq_lims[1] is None:
            freq_lims[1] = _thrd_center_freqs[-1]

        idx_lim = np.where((_thrd_center_freqs >= freq_lims[0]) & 
                                (_thrd_center_freqs <= freq_lims[1])
                                )[0]
        return _thrd_center_freqs[idx_lim]

    @staticmethod
    def minmax_freqs(freq_lims=[None,None]):
        """Retorna as frequências mínimas e máximas que correspondem a cada banda de terço de oitava 
        no intervalo especificado.

        Args:
            freq_lims (list, optional): frequências mínimas e máximas (intervalo fechado). Defaults to [None,None].

        Returns:
            np.ndarray: Array [n_bands, 2] contendo os limites da banda
        """
        global _thrd_minmax_freqs

               
        if freq_lims[0] is None:
            freq_lims[0] = 0
        if freq_lims[1] is None:
            freq_lims[1] = _thrd_center_freqs[-1]

        idx_lim = np.where((_thrd_center_freqs >= freq_lims[0]) & 
                                (_thrd_center_freqs <= freq_lims[1])
                                )[0]


        return _thrd_minmax_freqs[idx_lim]

    @staticmethod
    def get_band(freq=1000):
        """[QUEBRADO] Busca a banda da frequência especificada e retorna a frequência central,
        bem como os limites.

        * Fazer com que cheque a qual banda a frequência pertence. Ao invés de buscar a banda mais próxima

                Args:
            freq (int, optional): _description_. Defaults to 1000.

        Returns:
            _type_: _description_
        """
        center_freqs = ThirdOctaveBands.center_freqs()
        minmax_freqs = ThirdOctaveBands.minmax_freqs()
        idx = (abs(center_freqs-freq)).argmin()
        return center_freqs[idx], minmax_freqs[idx]
