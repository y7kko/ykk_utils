from ykk_utils.special_methods.SHMatrix import SHMatrixProcessor
from tessellation import SphereTessellator


def pk_downsampler(dir,pk,nverts=642,Nmax=30,
                   backend='cupy',chunksize=None):
    """Reduz

    Args:
        dir (_type_): _description_
        pk (_type_): _description_
        nverts (int, optional): _description_. Defaults to 642.
        Nmax (int, optional): _description_. Defaults to 30.
        backend (str, optional): _description_. Defaults to 'cupy'.
        chunksize (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    if chunksize is None:
        chunksize = int(pk.shape[1]/10)
    shp = (
        SHMatrixProcessor(dir=dir,pk_mtx=pk)
        .generate_kernel(Nmax)
        .decompose(backend   = backend, 
                    chunksize = chunksize
                    )
        )

    dir_rdc, _ = SphereTessellator(nverts).sphere
    pk_rdc = shp.project(dir=dir_rdc)
    pk_rdc *= (dir.shape[0]/dir_rdc.shape[0]) 
    return dir_rdc, pk_rdc
