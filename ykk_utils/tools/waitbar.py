import tqdm



def tqdm_flush():
    """Procura todas as waitbar ainda instânciadas e desliga elas,
    resolve o problema das waitbars do tqdm se encavalando
    """
    for barra in list(tqdm.tqdm._instances): 
        barra.close()
    tqdm.tqdm._instances.clear()
