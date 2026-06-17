#%%
import warnings


class arr_split2d:
    def __init__(self,array,step=None,axis=-1,return_limits=True):
        """Um simples iterador que divide uma matriz em vários
        slices de step amostras.

        Args:
            array (_type_): Array i want to slice
            step (int): number of steps i want to slice, if no value is passed, it will return the entire slice. Defaults to None
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
        
        if self.slice_axis >= self.ndim:
            raise ValueError('Algum problema em')
        # checking if step value is valid
        if not self.step:
            self.step = self.stop_max
        elif self.step >= self.stop_max:
            warnings.warn(f'step = {self.step} but input array have size {self.stop_max} in axis {self.axis}, clipping it to maximum value')
            self.step = self.stop_max

        #next soma step em start e stop, então para começar do 
        #chunk 1 vc precisa
        self.start = -self.step
        self.stop = 0
        self.iteration_end_flag = False

    def __iter__(self):
        return self
    
    def __next__(self):
        if self.iteration_end_flag:
            raise StopIteration

        self.start += self.step
        self.stop += self.step
        if self.stop >= self.stop_max:
            self.stop = self.stop_max
            self.iteration_end_flag = True


        arr_slice = cross_slice2d(self.ndim, self.start, self.stop,
                                        axis=self.axis
                                        )


        if not self.return_limits:
            return self.array[arr_slice]
        else:
            return tuple([[self.start,self.stop] ,
                         self.array[arr_slice]])


def cross_slice2d(ndim,start=None,stop=None,step=None,axis=-1):
    slice_axis = int(not axis) #slice em que ocorre as iterações

    arr_slice = [slice(None)]*ndim
    arr_slice[slice_axis] = slice(start,stop,step)
    return tuple(arr_slice)
