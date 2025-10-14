import numpy as np


class ISO9613:
    _pr = 101.325E3 #kpa
    _T0 = 293.15 #K

    @staticmethod
    def fr_O(h,pa,):
        pr = ISO9613._pr

        fr_O = (
            (pa/pr) *
            (24 + 4.04 * (10**4) * h * ((0.02+h)/(0.391+h)))
            )
        return fr_O

    @staticmethod
    def fr_N(T,h,pa):
        pr = ISO9613._pr
        T0 = ISO9613._T0        

        fr_N = (
            (pa/pr) * (T/T0)**(-1/2) * 
            (9 + 280*h * np.exp(-4.170*((T/T0)**(-1/3) - 1)))
            )
        return fr_N
    
    def alpha(f,T,h,pa=None,):
        """Calcula o coeficiente de atenuação do som por conta da atmosfera

        Args:
            f (double): frequência de interesse (Hz)
            T (double): Temperatura ambiente
            h (double): _description_
            pa (double, optional): _description_. Defaults to pr.

        Returns:
            _type_: _description_
        """
        pr = ISO9613._pr
        T0 = ISO9613._T0
        if pa is None:
            pa = pr

        fr_O = ISO9613.fr_O(h,pa)
        fr_N = ISO9613.fr_N(T=T,h=h,pa=pa)
        # Termo 1

        termo1 = 1.84E-11 * (pa/pr)**(-1) * (T/T0)**(1/2)

        #checar a multiplicação por 75
        termo2 = (T/T0)**(-5/2) * (
            0.01275 * ( np.exp(-2239.1/T)) * ( fr_O + ( (f**2) /fr_O))**(-1) + 
            0.1068 * ( np.exp(-3352.0/T) * ( fr_N + ( (f**2) /fr_N) )**(-1) )    
            )
        
        alpha = (8.686 * f**2)*(termo1 + termo2)
        return alpha
