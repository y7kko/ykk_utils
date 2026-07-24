#%%
import warnings

from ykk_utils.tools.waitbar import tqdm_flush
from ykk_utils.arraybackends import ArrayBackendManager
from tqdm import tqdm

class arr_split2d:
    def __init__(self,array,step=None,axis=-1,return_limits=True,waitbar=True,expected_signal_len=None):
        """Um simples iterador que divide uma matriz em vários
        slices de step amostras.

        Args:
            array (_type_): Array i want to slice
            step (int): number of steps i want to slice. Defaults to None
                - Step = None:
                    it will return the entire slice
                - Step = positive integer
                    step is directly set
                - Step = is float less than 1:
                    step is treated as a percentage of signal. Therefore,
                    step will be array.shape[axis]*step
                - if step is string:
                    The string must conform the format: 'backend:quantity',
                    where quantity defines the percentage of free memory to
                    be used for the operation. Example:
                        `arr_split2d(arr,'cupy:.5')` 
                        # 50% of free memory will be destinated to the operation
                    the following works too:
                        `arr_split2d(arr,'numpy:30%')`

            axis (int, optional): Axis where my signal exists. Defaults to -1.
            return_limits (bool, optional): If true, the object will return
                two arguments: 
                    - slice limits (list): [start,stop[ 
                    - array slice: array[:,start:stop], for example

        Example:
            ```
            M = np.zeros([30,250])
            for lims, m in arr_split2d(M,10,axis=1,return_limits=True):
                pass
                #irá me retornar 3 slices com shape [10,250]
            ```
        """
        self.array = array
        self.step = step
        self.axis = axis #where i want an entire slice
        self.return_limits = return_limits

        self.slice_axis = int(not self.axis) #slice em que ocorre as iterações
        self.ndim = self.array.ndim
        


        self.stop_max = self.array.shape[self.slice_axis]
        self.waitbar = waitbar
        if self.slice_axis >= self.ndim:
            raise ValueError('Algum problema em')
        # checking if step value is valid
        if not self.step:
            self.step = self.stop_max
        elif isinstance(self.step,str): #auto
            self.step = _autochunksize(self.step,array,axis,expected_signal_len=expected_signal_len)
        elif self.step<=1:
            self.step = int(array.shape[axis]*self.step)

        print('size per batch = ',self.step)
        if self.step >= self.stop_max:
            warnings.warn(f'step = {self.step} but input array have size {self.stop_max} in axis {self.axis}, clipping it to maximum value')
            self.step = self.stop_max




        #next soma step em start e stop, então para começar do 
        #chunk 1 vc precisa
        self.start = -self.step
        self.stop = 0
        self.iteration_end_flag = False

    def __iter__(self):
        self._waitbar_init()
        return self
    
    def __next__(self):
        if self.iteration_end_flag:
            self._waitbar_deinit()
            raise StopIteration

        self.start += self.step
        self.stop += self.step
        if self.stop >= self.stop_max:
            self.stop = self.stop_max
            self.iteration_end_flag = True


        arr_slice = cross_slice2d(self.ndim, self.start, self.stop,
                                        axis=self.axis
                                        )


        self._waitbar_add(self.stop-self.start)

        if not self.return_limits:
            return self.array[arr_slice]
        else:
            return tuple([[self.start,self.stop] ,
                         self.array[arr_slice]])



    def _waitbar_init(self):
        if self.step is not None and self.waitbar:
            tqdm_flush()
            self.wait = tqdm(total=self.stop_max)
        pass

    def _waitbar_add(self,val):
        val = int(val)
        if self.step is not None:
            self.wait.update(val)
        pass

    def _waitbar_deinit(self):
        if self.step is not None:
            self.wait.close()
        self.wait = None

def cross_slice2d(ndim,start=None,stop=None,step=None,axis=-1):
    """Dado um array n-dimensional, retorna um slice transversal
    ao eixo selecionado

    Exemplo:
        ```
            a = [[0,1,2],
                 [3,4,5],
                 [6,7,8]]
            slice = cross_slice2d(a.ndim,stop=1,axis=0)
            a[slice]
            >> [[0,1,2],[3,4,5]]
        ```
        Esse comportamento é útil para implementar funções
        em que o axis especificado define o eixo em que a operação
        percorre, mas também há a necessidade de gerar slices por
        sinal idependente.

    Args:
        ndim (_type_): _description_
        start (_type_, optional): _description_. Defaults to None.
        stop (_type_, optional): _description_. Defaults to None.
        step (_type_, optional): _description_. Defaults to None.
        axis (int, optional): _description_. Defaults to -1.

    Returns:
        _type_: _description_
    """
    slice_axis = int(not axis) #slice em que ocorre as iterações

    arr_slice = [slice(None)]*ndim
    arr_slice[slice_axis] = slice(start,stop,step)
    return tuple(arr_slice)

def _autochunksize(argument:str,array,axis,expected_signal_len=None):
    backend,value = argument.split(':')
    if value.endswith('%'):
        value = value[:-1]
        value = float(value)/100
    else:
        value = float(value)

    yp = ArrayBackendManager(backend).get_backend()
    free_bytes = yp.get_free_memory()
    bytes_to_use = free_bytes * value
    if expected_signal_len is None:
        signal_size = array.shape[axis]
    else:
        signal_size = expected_signal_len
    itemsize = array.itemsize
    bytes_per_signal = int(signal_size*itemsize)

    print(f'value {value}')
    print(f'Numero de samples por sinal {signal_size}')
    print(f'MiB livres {free_bytes/2**(20)}')
    print(f'MiB/sinal {bytes_per_signal/2**(20)}')
    print(f'MiB para usar {bytes_to_use/2**(20)}')
    slice_step = int(bytes_to_use/bytes_per_signal)
    slice_step = max(1,slice_step)
    return slice_step
