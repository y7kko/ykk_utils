#%%
import numpy as np
# import matplotlib.pyplot as plt
from ykk_utils.special_methods import sh_ft

#%%
(l,m) = (0,0)
analytical_c = .5*np.sqrt(1/np.pi)
analytical_r = .5*np.sqrt(1/np.pi)

computed_c = sh_ft.sph_wrapper(m,l,0,0,dtype=complex)
computed_r = sh_ft.sph_wrapper(m,l,0,0,dtype=float)
print(':: |Analitico - Computado|')
print(f'complex = {abs(computed_c-analytical_c)}')
print(f'real = {abs(computed_r-analytical_r)}')

#%%
(l,m) = (2,-1)
az,col,r = (0,0,1)
x,y,z = sh_ft.sph2cart(az,col,r)

analytical_c = (1/2)*np.sqrt(15/(2*np.pi)) * z*(x-1j*y)/(r**2)
analytical_r = (1/2)*np.sqrt(15/(np.pi))*y*z/(r**2)
computed_c = sh_ft.sph_wrapper(m,l,az,col,dtype=complex)
computed_r = sh_ft.sph_wrapper(m,l,az,col,dtype=float)

print(':: |Analitico - Computado|')
print(f'complex = {abs(computed_c-analytical_c)}')
print(f'real = {abs(computed_r-analytical_r)}')
