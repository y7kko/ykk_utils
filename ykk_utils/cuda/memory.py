"""
Ainda vou mudar esse nome,
mas diz respeito a métodos de gerenciamento de memória etc
"""

import cupy as cp
import numpy as np


def get_max_chksize(input:np.ndarray,axis,margin=.7):
    """Dado uma entrada e qual o indice que deve ser percorrido,
    a função calcula o número máximo de indices que é possível
    alocar na memória da GPU de uma única vez. Por padrão,
    o código reserva 30% da GPU para outras tarefas(`margin=.7`)

    Args:
        input (np.ndarray): O vetor de dados.
        axis (_type_): O eixo no qual eu pretendo iterar
        margin (float, optional): Quantidade relativa da memória da GPU
        que estou disposto a alocar. Defaults to .7.

    Returns:
        int: O número máximo de iterações que consigo jogar diretamente na
        GPU.
    """
    dev = cp.cuda.Device()
    free_bytes = dev.mem_info

    # Basicamente input[0,0,0, ..., :, ..., 0]
    array_mask = [0]*input.ndim
    array_mask[axis] = slice(None)
    per_iter_bytes = input[array_mask].nbytes

    return int(free_bytes*margin/per_iter_bytes)


