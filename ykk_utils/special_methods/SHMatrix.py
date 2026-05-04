import numpy as np
from . import sh_ft, sh_operations
from ..signal_analysis_utilities import dsp_funcs
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
        """Gera o kernel de decomposição

        Args:
            Nmax (int): Grau máximo de esférico harmônico no qual eu quero decompor
                O kernel possuirá tamanho (n_direcoes x (N+1)^2)

        Returns:
            self: Retorna a si mesmo, para encadeamento de funções
        """
        self.Nmax = Nmax
        self.Ydecomp =  sh_ft.generate_Y_kernel(azm=self.azm,
                                                elv=self.elv,
                                                N=Nmax,
                                                dtype=complex
                                                )
        self.nmmap = sh_ft.get_nm_map(N = Nmax)
        return self
        

    def decompose(self,):
        """Decompõe os dados de entrada em harmônicos esféricos.

        Returns:
            self: Retorna a si mesmo, para encadeamento de funções
        """
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


    def project(self,dir,Nmax=None) -> np.ndarray:

        #::: Condicionamento da entrada
        dir = np.asarray(dir)
        if len(dir.shape) == 1:
            dir = dir.reshape(1,3)

        if Nmax is None:
            Nmax = self.Nmax
            i_end = self.SH_decomp.shape[0]
        else:
            i_end = (Nmax+1)**2

        #::: Criação da base
        az, el, _ = sh_ft.cart2sph(dir[:,0],dir[:,1],dir[:,2])
        Yprojct = sh_ft.generate_Y_kernel(azm = az,
                                          elv = el,
                                          N = Nmax,
                                          dtype = complex
                                        )
        n_freqs = self.SH_decomp.shape[1]
        
        #::: Processamento
        p_projected = np.zeros([dir.shape[0],n_freqs],dtype=complex)
        for f in range(n_freqs):
            p_projected[:,f] = Yprojct @ self.SH_decomp[0:i_end, f]

        #::: Condicionamento da saida
        if p_projected.shape[0] == 1:
            p_projected = p_projected.flatten()

        return p_projected
    

    def _nm2idx(self,deg,ordr):
        """Dado um par (n,m), retorna o indíce correspondente na matriz
        de decomposição (self.SH_decomp) 

        Args:
            deg (int): O grau(n) [0, Nmax]
            ordr (int): A ordem [-Nmax, Nmax]

        Returns:
            int: O indíce correspondente ao par (n,m)
        """
        if hasattr(self,'SH_decomp'):
            idx = np.where((self.nmmap[:,0] == deg) & (self.nmmap[:,1] == ordr))[0]
            if not (len(idx) == 0):
                return idx
            else:
                raise ValueError('(n,m) pair not defined')
        else:
            raise ValueError('Decomposição em harmônicos esféricos não realizada')


    @property
    def nm(self,):
        """Acessar os resultados de decomposição usando nm como indexadores.
            Exemplo:
                obj.nm[0,0] #retorna A00(f) = self.SH_decomp[0,:]
        """
        return nmIndexer(self)


class nmIndexer:
    """Serve para facilitar acesso aos dados da decomposição.
    Exemplo:
        SHMatrixProcessor.nm[0,0] #retorna A00(f)
    """
    def __init__(self,parent):
        self.parent:SHMatrixProcessor = parent


    def __getitem__(self, key):
        n,m = key
        idx = self.parent._nm2idx(n,m)

        if len(idx) == 1:
            return self.parent.SH_decomp[idx,:].flatten()
        else: #Array slice ou algo assim, infelizmente não impementei
            return self.parent.SH_decomp[idx,:]


    def __setitem__(self, key, value):
        n,m = key
        idx = self.parent._nm2idx(n,m)
        self.parent.SH_decomp[idx,:] = value
