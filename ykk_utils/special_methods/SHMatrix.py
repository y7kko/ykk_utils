import numpy as np
from . import sh_ft, sh_operations
from ..signal_analysis_utilities import dsp_operations
from tqdm import tqdm
from ..SmallScripts import tqdm_flush


class SHMatrixProcessor:
    def __init__(self, pk_mtx, dir, pk_freq=None, fs=None):
        """Uma classe que recebe uma matriz de pressões variando de
        acordo com a frequência, definidas em uma esfera, e realiza a
        decomposição em ondas planas da matriz.

        Args:
            pk_mtx (ndarray): Matriz de pressões com shape (n_dir, freq)
            dir (ndarray): Matriz de coordenadas(cartesianas) com shape (n_dir, 3)
            ---
            Não lembro qual o motivo de eu declarar isso... Por enquanto não foi usado
            pk_freq (ndarray): Vetor de frequências de shape (freq)
            fs (float): Frequência de amostragem
        """
        self.pk_mtx = pk_mtx
        
        self.dir = dir
        # Converter em dir coordenadas esféricas
        self.azm, self.elv, _ = sh_ft.cart2sph(
            x = self.dir[:,0],
            y = self.dir[:,1],
            z = self.dir[:,2]
            )
        
        # self.pk_freq = pk_freq # frequencia incompleta ainda
        # self.fs = fs
        pass
    
    def generate_kernel(self,Nmax):
        self.Nmax = Nmax
        self.Ydecomp =  sh_ft.generate_Y_kernel(azm=self.azm,
                                                elv=self.elv,
                                                N=Nmax,
                                                dtype=complex
                                                )
        return self
        
    def decompose(self,):
        if not hasattr(self,'Ydecomp'):
            raise ValueError("Kernel não inicializado, utilize generate_kernel()")
        n_dirs  = self.pk_mtx.shape[0]
        n_freqs = self.pk_mtx.shape[1]

        n_degordr = (self.Nmax+1)**2

        solution = np.zeros([n_degordr, n_freqs],dtype=complex)
        tqdm_flush()
        bar = tqdm(total = n_freqs, 
                    desc = 'Decomposing...')
        
        # Eventualmente isso aqui vai mudar...
        for f in range(n_freqs):
            solution[:,f] = sh_ft.solve_LSQ(
                                            Kernel = self.Ydecomp,
                                            pk_input = self.pk_mtx[:,f],
                                            return_all = False
                                        )
            bar.update(1)

        self.SH_decomp = solution
        return self

    def project(self,dir):
        
        if len(dir.shape) == 1:
            dir = dir.reshape(1,3)

        az, el, _ = sh_ft.cart2sph(dir[:,0],dir[:,1],dir[:,2])
        Yprojct = sh_ft.generate_Y_kernel(azm=az,
                                        elv=el,
                                        N=self.Nmax,
                                        dtype=complex
                                    )
        n_freqs = self.SH_decomp.shape[1]
        
        p_projected = np.zeros([dir.shape[0],n_freqs],dtype=complex)
        for f in range(n_freqs):
            p_projected[:,f] = np.matmul(Yprojct,
                                         self.SH_decomp[:,f]
                                         )

        return p_projected
