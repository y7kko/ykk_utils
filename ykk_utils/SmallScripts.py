"""
Alguns scripts que fazem coisas uteis no codigo, mas que também não se classificam em nd
"""
try:
    from IPython.display import display,Audio, Markdown
except:
    pass

import tqdm



def tqdm_flush():
    """Procura todas as waitbar ainda instânciadas e desliga elas,
    resolve o problema das waitbars do tqdm se encavalando
    """
    for barra in list(tqdm.tqdm._instances): 
        barra.close()
    tqdm.tqdm._instances.clear()


def audio(data,fs,normalize=True,**kwargs):
    """Na verdade é uma chamada direta pro display.Audio

    Args:
        data (_type_): _description_
        fs (_type_): _description_
        normalize (bool, optional): _description_. Defaults to True.
    """
    audio_kw = {**{
                    'data':data,
                    'rate':fs,
                    'normalize':normalize
                    },
                **kwargs
                }
    audio_instance = Audio(**audio_kw)
    display(audio_instance)
