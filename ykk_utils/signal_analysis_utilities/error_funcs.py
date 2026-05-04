""" Funções para computar erro
"""


import numpy as np
import matplotlib.pyplot as plt


def nmse(x_sol, x_truth):
    """ returns the NMSE (normalized mean squared error)

    Parameters
    ----------
        x_sol : numpy 1darray
            solution
        x_sol : numpy 1darray
            ground truth
    Returns
    -------
        nnse : float
            estimated NMSE
    """
    nmse = (np.linalg.norm(x_sol-x_truth)/np.linalg.norm(x_truth))**2
    return nmse

def mae(x_sol, x_truth):
    """ returns the MAE (nmean absolute error)

    Parameters
    ----------
        x_sol : numpy 1darray
            solution
        x_sol : numpy 1darray
            ground truth
    Returns
    -------
        mae : float
            estimated MAE
    """
    mae = np.linalg.norm(x_sol-x_truth)
    return mae

def nmse_freq(x_sol, x_truth):
    """ returns the NMSE vs freq (normalized mean squared error)

    Parameters
    ----------
        x_sol : numpy ndarray
            solution arraged in Nvals x Nfreq 
        x_sol : numpy ndarray
            ground truth arraged in Nvals x Nfreq 
    Returns
    -------
        nnse : nympy 1dArray
            estimated NMSE vs freq
    """
    _, nfreq = x_sol.shape
    nmse_freq = np.zeros(nfreq)
    for jf in np.arange(nfreq):
        nmse_freq[jf] = nmse(x_sol[:,jf], x_truth[:,jf])
    return nmse_freq


def ykk_nmse_freq(x_sol, x_truth):
    """ returns the NMSE vs freq (normalized mean squared error)

    Parameters
    ----------
        x_sol : numpy ndarray
            solution arraged in Nvals x Nfreq 
        x_sol : numpy ndarray
            ground truth arraged in Nvals x Nfreq 
    Returns
    -------
        nnse : nympy 1dArray
            estimated NMSE vs freq
    """
    nfreq = len(x_sol)
    nmse_freq = np.zeros(nfreq)
    nmse_freq[:] = ykk_nmse(x_sol[:],x_truth[:])
    # for jf in np.arange(nfreq):
    #     nmse_freq[jf] = ykk_nmse(x_sol[:,jf], x_truth[:,jf])
    return nmse_freq

def ykk_nmse(x_sol, x_truth):
    """ returns the NMSE (normalized mean squared error)

    Parameters
    ----------
        x_sol : numpy 1darray
            solution
        x_sol : numpy 1darray
            ground truth
    Returns
    -------
        nnse : float
            estimated NMSE
    """
    nmse = (
        (np.abs(x_sol) - np.abs(x_truth)) / np.abs(x_truth)
        )**2
    return nmse

class Efren:
    """Conjunto de métodos que computa as métricas de erro propostos por Fernandez Grande

    ref: Fernandez Grande, E. (2016). Sound field reconstruciton using a spherical microphone array. 
         Journal of the Acoustical Society of America, 139(3), 1168-1178. 
         https://doi.org/10.1121/1.4943545
    """

    @staticmethod
    def freq_error(x_sol, x_truth):
        """ Retorna o erro da média espacial por frequência
        (Métrica proposta por Fernandez Grande)

        Args:
            x_sol (_type_): Aproximação
            x_truth (_type_): Ground truth

        Returns:
            error: o erro estimado (%)
        """

        #Caso seja unidimensional, transformar em [1 pt, n_freq]
        x_sol   = _single_point_correction(x_sol)
        x_truth = _single_point_correction(x_truth)

        n_freq = x_sol.shape[1]

        error = np.zeros(n_freq)
        for jf in np.arange(n_freq):
            error[jf] = Efren.epsilon(x_sol[:,jf], x_truth[:,jf])
        return error

    @staticmethod
    def epsilon(x_sol, x_truth):
        """ Retorna o erro relativo
        (Métrica proposta por Fernandez Grande)

        Parameters
        ----------
            x_sol : numpy 1darray
                solution
            x_sol : numpy 1darray
                ground truth
        Returns
        -------
            nnse : float
                estimated NMSE
        """
        eps = np.linalg.norm(x_truth-x_sol)/np.linalg.norm(x_truth)
        return eps
    
    def spatial_epsilon(x_sol, x_truth):
        eps = np.abs(x_truth-x_sol)/np.abs(x_truth)
        return eps
    @staticmethod
    def foo():
        print('bar')
        
def _single_point_correction(arr):
    """Usando np.atleast_2d e depois garantindo que seja coluna"""
    arr_2d = np.atleast_2d(arr)
    if arr_2d.shape[1] == 1:  # Se ficou como linha [n, 1]
        return arr_2d.T  # Transpõe para coluna [1, n]
    return arr_2d
