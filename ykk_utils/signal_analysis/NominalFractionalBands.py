import numpy as np
import os

_oct_center_freqs = None
_oct_minmax_freqs = None
_thrd_center_freqs = None
_thrd_minmax_freqs = None


def _load_file(filename):
    """Carrega um arquivo .csv no subfolder 'data/'

    Args:
        filename (str): _description_

    Returns:
        np.ndarray: O vetor contido no .csv
    """
    module_dir = os.path.dirname(__file__)
    path= os.path.join(module_dir,'ISO3_banddata',filename)
    return np.loadtxt(path,delimiter=',')
    

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
        if _oct_center_freqs is None:
            _oct_center_freqs = _load_file('oct.csv')
            
        if freq_lims[0] is None:
            freq_lims[0] = 0
        if freq_lims[1] is None:
            freq_lims[1] = _oct_center_freqs[-1]

        idx_lim = np.where((_oct_center_freqs >= freq_lims[0]) & 
                                (_oct_center_freqs <= freq_lims[1])
                                )[0]
        return _oct_center_freqs[idx_lim]

    @staticmethod
    def minmax_freqs(): #Faz caching a nivel de modulo
        """Retorna as frequências mínimas e máximas que correspondem a cada banda de terço de oitava 
        no intervalo especificado.

        Args:
            freq_lims (list, optional): frequências mínimas e máximas (intervalo fechado). Defaults to [None,None].

        Returns:
            np.ndarray: Array [n_bands, 2] contendo os limites da banda
        """

        global _oct_minmax_freqs

        if _oct_minmax_freqs is None:
            _oct_minmax_freqs = _load_file('oct_minmax.csv')
        return _oct_minmax_freqs
    
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
        if _thrd_center_freqs is None:
            _thrd_center_freqs = _load_file('third_oct.csv')

        
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
        if _thrd_minmax_freqs is None:
            _thrd_minmax_freqs = _load_file('third_oct_minmax.csv')

               
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
