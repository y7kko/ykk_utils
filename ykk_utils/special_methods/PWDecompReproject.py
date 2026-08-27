import numpy as np
from tqdm import tqdm
from ykk_utils.tools.waitbar import tqdm_flush
from ykk_utils.arraybackends.array_slicetools import arr_split2d,cross_slice2d
from ykk_utils.arraybackends import ArrayBackendContext,ArrayBackendManager
class PWDecompReproj:
    def __init__(self,dir,k0,pk):
        """Recebe dados de uma decomposição em ondas planas e projeta em uma
        coordenada real.

        \sum P(k0,theta,phi) -> p(x,y,z)

        Args:
            dir (_type_): Vetor de coordenadas
            k0 (_type_): Vetor de módulo do número de onda
            pk (_type_): Matriz de coeficientes de cada onda plana
        """
        self.dir = dir
        self.k0 = k0
        self.pk = pk


    def project(self, coord):
        """ Reconstruct the sound pressure and particle velocity at a receiver object

        Reconstruct the pressure and particle velocity at a set of desired field points.
        This can be used on impedance estimation or to plot spatial maps of pressure,
        velocity, intensity.

        The steps are: (i) - Get the scaled version of the propagating directions;
        (ii) - form the new sensing matrix; (iii) - compute p and u.

        Parameters
        ----------
        receivers : object (Receiver)
            contains a set of field points at which to reconstruct
        compute_uxy : bool
            Whether to compute x and y components of particle velocity or not (Default is False)
        """
        coord = np.asarray(coord)
        if len(coord.shape) == 1:
            coord = coord.reshape(1,3)
            
        self.p_recon = np.zeros((coord.shape[0], len(self.k0)), 
                                dtype=complex)

        # Loop over frequency
        tqdm_flush()
        bar = tqdm(total = len(self.k0), desc = 'Reconstructing sound field...')
        for f_idx, k0 in enumerate(self.k0):
            # get the scaled version of the propagating directions
            k_p = k0 * self.dir
            # Form the new sensing matrix
            h_mtx = np.exp(-1j*coord @ k_p.T)
            # compute P and U
            
            self.p_recon[:,f_idx] = h_mtx @ self.pk[:,f_idx]
            bar.update(1)
        bar.close()
        if self.p_recon.shape[0] == 1:
            self.p_recon = self.p_recon.flatten() 
        return self.p_recon
    
    def project2(self, coord,chunk_size=500,backend='numpy'):
        """ Reconstruct the sound pressure and particle velocity at a receiver object

        Reconstruct the pressure and particle velocity at a set of desired field points.
        This can be used on impedance estimation or to plot spatial maps of pressure,
        velocity, intensity.

        The steps are: (i) - Get the scaled version of the propagating directions;
        (ii) - form the new sensing matrix; (iii) - compute p and u.

        Parameters
        ----------
        receivers : object (Receiver)
            contains a set of field points at which to reconstruct
        compute_uxy : bool
            Whether to compute x and y components of particle velocity or not (Default is False)
        """
        coord = np.asarray(coord)
        if len(coord.shape) == 1:
            coord = coord.reshape(1,3)
            
        self.p_recon = np.zeros((coord.shape[0], len(self.k0)), 
                                dtype=complex)

        k0 = self.k0
        dir = self.dir[np.newaxis,...]
        ynp = ArrayBackendManager(backend).get_backend_namespace()
        yp = ArrayBackendManager(backend).get_backend()

        coord = yp.to_backend(coord)
        for lims,k0 in arr_split2d(array=k0,step=chunk_size,):
            k_p = k0[...,np.newaxis,np.newaxis]*dir # k (n,3)

            
            with ArrayBackendContext(backend) as yp:
                k_p_bck = yp.to_backend(k_p)
                exp_arg = ynp.einsum('ij,lkj->lik',-1j*coord,k_p_bck) #(M,3) * k (3,n) ->k M,N
                h_mtx = ynp.exp(exp_arg) # k M,N
                slc = slice(lims[0],lims[1])
                p_recon = ynp.einsum('ijk,ki->ji',h_mtx,self.pk[:,slc])            
                self.p_recon[:,slc] = yp.to_numpy(p_recon)

        self.p_recon= self.p_recon.squeeze()
        return self.p_recon
