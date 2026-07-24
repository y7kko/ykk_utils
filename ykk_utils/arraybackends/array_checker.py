import numpy as np
try:
    import cupy as cp
except:
    pass

def arrsize(arr,unit='MB'):
    div = 1
    if unit.upper() == 'KB':
        div = 2**10
    elif unit.upper() == 'MB':
        div = 2**20    
    elif unit.upper() == 'GB':
        div = 2**30    
    print(arr.nbytes/div)


def checkVals(arr,):
    print(f"Forma: {arr.shape}")
    print(f"Dtype: {arr.dtype}")
    print(f"Min: {arr.min()}, Max: {arr.max()}")
    print(f"Tem NaN: {np.isnan(arr).any()}")
    print(f"Tem Inf: {np.isinf(arr).any()}")
    print(f"Memória (MB): {arr.nbytes / 1024 / 1024:.2f}")
