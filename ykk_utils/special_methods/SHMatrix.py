import numpy as np
from . import sh_ft, sh_operations
from ..signal_analysis_utilities import dsp_operations
from tqdm import tqdm
from ..SmallScripts import tqdm_flush
class SHMatrixProcessor:
    def __init__(self, pk_mtx, dir, pk_freq, fs):
        self.pk_mtx = pk_mtx
        
        self.dir = dir
        # Converter em dir coordenadas esféricas
        self.azm, self.elv, _ = sh_ft.cart2sph(
            x = self.dir[:,0],
            y = self.dir[:,1],
            z = self.dir[:,2]
            )
        
        self.pk_freq = pk_freq # frequencia incompleta ainda
        self.fs = fs
        pass
    
    def generate_kernel(self,Nmax):
        self.Ykernel =  sh_ft.generate_Y_kernel(azm=self.azm,
                                                elv=self.elv,
                                                N=Nmax,
                                                dtype=complex
                                                )
        self.Nmax = Nmax
        
    def decompose(self,localNmax=None):
        if not hasattr(self,'Ykernel'):
            raise ValueError("Kernel não inicializado, utilize generate_kernel()")
        n_dirs  = self.pk_mtx.shape[0]
        n_freqs = self.pk_mtx.shape[1]
        if localNmax is None:
            n_degordr = (self.Nmax+1)**2
        else:
            n_degordr = (localNmax+1)**2


        solution = np.zeros([n_degordr, n_freqs],dtype=complex)
        tqdm_flush()
        bar = tqdm(total = n_freqs, 
                    desc = 'Decomposing...')
        # Eventualmente isso aqui vai mudar...
        for f in range(n_freqs):
            solution[:,f] = sh_ft.solve_LSQ(
                                            Kernel = self.Ykernel,
                                            pk_input = self.pk_mtx[:,f],
                                            return_all = False
                                        )[:n_degordr]
            bar.update(1)

        self.SH_decomp = solution
        return self.SH_decomp
