import numpy as np

from ykk_utils import dsp_funcs as dsp
from ykk_utils.arraybackends import ArrayBackendManager,ArrayBackendContext
from ykk_utils.arraybackends import array_slicetools as arrslice

"""
Trata o problema de detecção de ruído de fundo como um problema de knee point.
A principal diferença é que não há regressões lineares.
    - Como no método de lundeby, o sinal é suavizado por média em blocos de 10---50ms
    - Um novo intervalo de suavização é determinado por meio do coeficiente angular médio
    entre o ponto máximo da curva e dois pontos não equidistantes. O novo intervalo
    entre blocos é escolhido de forma a obter entre 3---5 pontos a cada 10 dB de decaimento.

:: O sinal em sua segunda suavização serve como dado de entrada para uma versão
   simplificada do algoritmo Kneedle.
    - A suavização é realizada por meios do rms em blocos(comparado à suavização)
      por splines, do paper original.
    - x e y são normalizados pelo máximo;
    - É traçada uma reta entre o primeiro e ultimo ponto do sinal; e
    - O piso de ruído é a região em que a curva suavizada apresenta maior distância
      perpendicular à reta.

    Embora o algoritmo original determina máximos locais e introduz métrica de
    sensibilidade de detecção, sabe-se que em IR bem comportada há ponto de 
    inflexão visualmente distinto.

Prós:
    - Simplifica implementação e custo computacional. Além do método realizar menos
      operações sobre o conjunto de dados, o algoritmo é determinístico, sendo
      necessário sempre uma única iteração para determinar o valor final;
    - Os calculos são, em geral, vetorizáveis;
    - Reafirmando o tópico anterior, o método não é iterativo, o que torna seu custo
      computacional mais previsível; e
    - O meu problema apresenta definição matemática clara.
Problemas:
    - IRs truncadas ou de alta variabilidade(regiões de baixa frequência) apresentam
      comportamento errático. Embora a condição também represente caso indefinido para 
      o método de Lundeby, o fato do algoritmo começar da cauda e iterar até estabilizar
      faz com que ele sempre determine um knee point mais próximo ao final da resposta.
"""


# modified lundeby method
def modified_kneedle(ht,fs,axis=-1,backend='numpy',chunk_size=None):
    
    dB = lambda x: 10*np.log10(x)    
    t = dsp.tvec(ht.shape[axis],fs)
    n_signals = ht.shape[not axis]
    for lims, chunk in arrslice.arr_split2d(ht, chunk_size, axis=axis,waitbar=True):
        # idxs = arrslice.cross_slice2d(edc_mtx.ndim, lims[0],lims[1],axis=axis)

        with ArrayBackendContext(backend) as yp:
            #iteration 1
            ynp = ArrayBackendManager(backend).get_backend_namespace()
            chk_size = int(10E-3*fs)
            ht_chk, t_chk = _chunk_divider(chunk,t,axis=axis,chk_size=chk_size,backend=backend)

            noise_est_len = int(len(t_chk)*.01) #os ultimos 10% do sinal são compostos de ruído

            
            noise_slice = [slice()]*ht_chk.ndim
            noise_slice[axis] = slice(-noise_est_len,None)
            noise_est = ynp.sqrt(ynp.mean(ht_chk[tuple(noise_slice)]**2,axis=axis))
            # por enquanto
            noise_level = dB(noise_est**2) #(n_signals)

            if axis==-1: #para realizar broadcast
                noise_level = noise_level.reshape(-1,1)

            reg_idx = dB(ht_chk**2) >= (noise_level + 5)
            
            # reg_idx = np.where(
            # dB(ht_chk**2)>=(dB(noise_est**2)+5)
            # )[0]
            

            a, b = np.polyfit(x=t_chk[reg_idx],
                            y=dB(ht_chk[reg_idx]), deg=1)
            chk_size = int((-10/(5*a))*fs) #(5/10) blocks/dB

            raise NotImplementedError('Ainda não terminei de implementar')

            ht_chk = dsp.chunk_split(ht,chk_size=chk_size,discard_padded=True)
            ht_chk = np.sqrt(np.mean(ht_chk**2,axis=1))
            t_chk = dsp.chunk_split(t,chk_size=chk_size,discard_padded=True)
            t_chk = np.mean(t_chk,axis=1)

            knee_idx = _knee_maxchord(t_chk,ht_chk)

            # Ajustar uma reta entre t=0 e tn tal que h^2(tn)=noise+10dB.
            # A partir disso, extrapolar após região de truncamento para
            # compensar o truncamento por ruído
            max_reg_idx = np.where(
                    dB(ht_chk) >= #h(t)
                    dB(np.sum(ht_chk[knee_idx:]**2)) + 10 #noise estimation + 10dB
                )[0][-1]
            a, b = np.polyfit(x=t_chk[:max_reg_idx],
                            y=dB(ht_chk[:max_reg_idx]), deg=1)
            # O valor de truncamento
            Ccomp = np.sum(10**((a*t_chk[knee_idx:]+b)/10))


    raise NotImplementedError('Ainda não terminei de implementar')
    # Parei aqui
    # yp.chunk_split2d(ht,chk_size=chk_size,discard_padded=True)
    ht_chk = dsp.chunk_split(ht,chk_size=chk_size,discard_padded=True)
    ht_chk = np.sqrt(np.mean(ht_chk**2,axis=1))
    t_chk = dsp.chunk_split(t,chk_size=chk_size,discard_padded=True)
    t_chk = np.mean(t_chk,axis=1)

    noise_est_len = int(len(t_chk)*.01)
    noise_est = np.sqrt(np.mean(ht_chk[-noise_est_len:]**2))

    reg_idx = np.where(
        dB(ht_chk**2)>=(dB(noise_est**2)+5)
        )[0]

    a, b = np.polyfit(x=t_chk[reg_idx],
                    y=dB(ht_chk[reg_idx]), deg=1)

    chk_size = int((-10/(5*a))*fs) #(5/10) blocks/dB
    ht_chk = dsp.chunk_split(ht,chk_size=chk_size,discard_padded=True)
    ht_chk = np.sqrt(np.mean(ht_chk**2,axis=1))
    t_chk = dsp.chunk_split(t,chk_size=chk_size,discard_padded=True)
    t_chk = np.mean(t_chk,axis=1)

    knee_idx = _knee_maxchord(t_chk,ht_chk)

    # Ajustar uma reta entre t=0 e tn tal que h^2(tn)=noise+10dB.
    # A partir disso, extrapolar após região de truncamento para
    # compensar o truncamento por ruído
    max_reg_idx = np.where(
            dB(ht_chk) >= #h(t)
            dB(np.sum(ht_chk[knee_idx:]**2)) + 10 #noise estimation + 10dB
        )[0][-1]
    a, b = np.polyfit(x=t_chk[:max_reg_idx],
                    y=dB(ht_chk[:max_reg_idx]), deg=1)
    # O valor de truncamento
    Ccomp = np.sum(10**((a*t_chk[knee_idx:]+b)/10))
    
    return t_chk[knee_idx], Ccomp

def _knee_maxchord(x,y,axis=-1):
    """Retorna indíce onde se encontra knee point utilizando 
    implementação (empírica) de TMDSM. O método considera a inflexão 
    como o ponto de maior distância perpendicular à um segmento de 
    reta formado por (x0,y0) e (xn,yn), em que n representa o 
    último par ordenado do meu conjunto de dados.

    A distância entre ponto e reta, então, é determinada por
    formula clássica da geometria analítica [1]. Como os dados são
    normalizados a priori, e a magnitude da distância é irrelevante ao problema, 
    pode-se reduzir a equação
        ```
        d = abs((y[-1]-y[0])*x -(x[-1]-x[0])*y + x[-1]*y[0] -y[-1]*x[0])
        d /= np.sqrt((y[-1] - y[0])**2 + (x[-1] - x[0])**2)
        return d.argmax()
        ```
    por
        ```
        d = abs(x+y).argmin(),
        ```
    Args:
        x (ndarray): Valores de x
        y (ndarray): Valores de y

    Returns:
        int: índice em que se encontra ponto de inflexão geométrico.

    References:
        Ref [1]: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
    """
    np_kw = dict(axis=axis,keepdims=True)
    # Normalizing x and y
    x = (x - np.min(x,**np_kw)) / (np.max(x,**np_kw) - np.min(x,**np_kw))
    y = (y - np.min(y,**np_kw)) / (np.max(y,**np_kw) - np.min(y,**np_kw))    
    return abs(x+y).argmin()

def _chunk_divider(ht:np.ndarray,t:np.ndarray,axis:int,chk_size:int,backend:str):
        # modulo das minhas funções
        yp = ArrayBackendManager(backend).get_backend()
        # namespace padrão (backend = 'numpy' retorna np, por ex)
        ynp = ArrayBackendManager(backend).get_backend_namespace()
        
        # Separar em blocos e calcular rms por bloco
        ht_rms = yp.chunk_split2d(ht,chk_size=chk_size,
                                axis=axis,discard_padded=True
                                )
        ht_rms = ynp.mean(ht_rms**2,axis=-1)

        #separar em blocos e calcular média por bloco
        t_mean = yp.chunk_split2d(t,chk_size=chk_size,
                                axis=axis,discard_padded=True
                                )
        t_mean = ynp.mean(t_mean,axis=1)
        return ht_rms,t_mean
