"""
Funções para computar a decomposição em harmônicos esféricos
"""
import numpy as np
from scipy.special import sph_harm


def cart2sph(x, y, z, positive_azm=False, steady_elv=False):
    """Conversion of cartesian to spherical coordinates.
        Essa função foi tirada do Spaudiopy, preferi apenas reimplementar
        para evitar a criação de mais uma dependência. 
        Eventualmente pretendo abrir as equações e implementar sozinho.
    
        MIT License
        Copyright (c) 2025 Christoph Hold
        Source: https://github.com/chris-hld/spaudiopy (v0.2.0)
        DOI: 10.5281/zenodo.15384855

    ## Args:
        x (_type_): 
            _description_
        y (_type_): 
            _description_
        z (_type_): 
            _description_
        positive_azm (bool, optional): 
            Convenção do azimute ([-pi, pi] -> [0, 2pi). Defaults to False.
        steady_elv (bool, optional): 
            Nunca deixar a elevação chegar ao 0 absoluto(pra evitar divisão por zero). Defaults to False.

    ## Returns:
        azm (ndarray): 
            Azimute
        elv (ndarray): 
            Elevação (colatitude)
        r   (ndarray): 
            Raio
    """

    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)
    r = np.sqrt(x**2 + y**2 + z**2)
    azm = np.arctan2(y, x)
    
    if positive_azm:
        azm = azm % (2 * np.pi)  # [-pi, pi] -> [0, 2pi)
    elv = np.arccos(z / r) if not steady_elv else \
        np.arccos(z / np.clip(r, 10e-15, None))
    return azm, elv, r

def sph2cart(azi, zen, r=1):
    """ Conversion of spherical to cartesian coordinates.
        
        Essa função foi tirada do Spaudiopy, preferi apenas reimplementar
        para evitar a criação de mais uma dependência. 
        Eventualmente pretendo abrir as equações e implementar sozinho.
    
        MIT License
        Copyright (c) 2025 Christoph Hold
        Source: https://github.com/chris-hld/spaudiopy (v0.2.0)
        DOI: 10.5281/zenodo.15384855


    """
    azi = np.asarray(azi)
    zen = np.asarray(zen)
    r = np.asarray(r)
    x = r * np.cos(azi) * np.sin(zen)
    y = r * np.sin(azi) * np.sin(zen)
    z = r * np.cos(zen)
    return x, y, z



def generate_Y_kernel(azm:np.ndarray,elv:np.ndarray,N=7,dtype=None):
    """Recebe um array de coordenadas esféricas em uma esfera unitária
    e calcula um Kernel de esféricos harmônicos do grau 0 até N.

    Args:
        azm (np.ndarray): Azimute(Longitude) - variando de [0  , 2pi]
        elv (np.ndarray): Elevação(Colatitude) - variando de [0, pi] 
        N (int, optional): Grau máximo de esférico harmônico. Defaults to 7.
    
    Returns:
        Kernel (np.ndarray): Matriz com dimensões [número de direções x (N+1)^2]
                            Tenha em mente que a sequência é
                            [Y00, Y-11, Y01, Y11, ... , Ymn]^T
    """

    Kernel = np.zeros([len(azm), (N+1)**2],
                    dtype=dtype
                    )

    counter = 0
    for n in range(0,N+1):
        for m in range(-n,n+1):
            Ymn = sph_harm(m,n,azm,elv)
            Kernel[:,counter] = Ymn
            counter+=1

    return Kernel


def solve_LSQ(Kernel,pk_input,return_all=False):
    """Resolve um problema utilizando Least-Squares optimization

    Args:
        Kernel (np.ndarray): O "modelo de mundo" [número de direções x (N+1)^2]
        pk_input (np.ndarray): Os dados que você quer ajustar [número de direções,]
        return_all (bool, optional): Caso true, todos os returns do linalg.lstsq serão retornados ao caller. Defaults to False.

    Returns:
        ndarray: Um vetor de shape [(N+1^2),]
    """
    Amn, res, rank, singular = np.linalg.lstsq(Kernel,
                                           pk_input,rcond=None)
    if return_all:
        return Amn, res, rank, singular
    
    return Amn


def get_nm_map(N):
    """Retorna os pares (nm) correspondentes de cada linha do
    kernel

    Args:
        N (int): grau máximo

    Returns:
        lm_map (np.ndarray): O mapa
    """
    nm_map = np.zeros([(N+1)**2,2],
                      dtype=int
                    )

    counter = 0
    for n in range(0,N+1):
        for m in range(-n,n+1):
            nm_map[counter, 0] = n
            nm_map[counter, 1] = m
            counter += 1
    return nm_map
