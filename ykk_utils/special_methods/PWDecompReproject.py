import numpy as np
from tqdm import tqdm
from ykk_utils.SmallScripts import tqdm_flush
class PWDecompReproj:
    def __init__(self,dir,k0,pk):
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
        if len(coord.shape) == 1:
            coord = coord.reshape(1,3)
            
        self.p_recon = np.zeros((coord.shape[0], len(self.k0)), 
                                dtype=complex)

        # Loop over frequency
        tqdm_flush()
        bar = tqdm(total = len(self.k0), desc = 'Reconstructing sound field...')
        for f_idx, k in enumerate(self.k0):
            # get the scaled version of the propagating directions
            k_p = k * self.dir
            # Form the new sensing matrix
            h_mtx = np.exp(-1j*coord @ k_p.T)
            # compute P and U
            self.p_recon[:,f_idx] = h_mtx @ self.pk[:,f_idx]
            bar.update(1)
        bar.close()
        return self.p_recon

