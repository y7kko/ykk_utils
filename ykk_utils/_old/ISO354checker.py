import numpy as np

class ISO354checker:
    @staticmethod
    def checkISO(aresta,nX,nY):
        if np.size(aresta) == 1:
            aresta = [aresta, aresta]
        
        L = aresta[0]*nX
        h = aresta[1]*nY


        area = L*h
        ratio = [L/h, h/L]
        # True nos dois se está dentro da 354
        print('::Requisito de área')
        print(f'A = {area}, A>10 - {12.01 > area > 10.01}') #
        print('::Requisito de proporção')
        print(f'L/h = {min(ratio)} - {(1 > L/h > 0.7) or (1 > h/L > 0.7)}')
        print('dimensões')
        print(f'L= {L:.2f} h = {h}')    
