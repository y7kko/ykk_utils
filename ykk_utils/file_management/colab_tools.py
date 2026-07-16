import h5py
import warnings
from receivers import Receiver
try:
    import pyperclip
except:
    pass



class colabrw():
    """Classe especifica para ler e escrever arrays a serem passados para o colab

    Returns:
        _type_: _description_
    """
    @staticmethod
    def dict2hdf5(filename,path,dataset,metadata:dict={}):
        filePath=f'{path}{filename}'
        file = h5py.File(filePath,'w')
        for key,val in dataset.items():
            file.create_dataset(name=key,
                                data=val)
        
        if len(metadata) == 0:
            warnings.warn('Não há metadados no arquivo')
        else:
            for key,val in metadata.items():
                file.attrs[key] = val 

        file.close()
        try:
            pyperclip.copy(filename)
            print("nome do arquivo exportado para a área de transferência")
        except:
            pass

        print(filename)



    @staticmethod
    def cloud_read(filename,path):
        """Importar .hdf5(.colabinput) e transformar em um conjunto de variáveis compatível
        com o código do colab

        Args:
            filename (_type_): _description_
            path (_type_): _description_

        Returns:
            _type_: _description_
        """
        file = h5py.File(f"{path}{filename}", 'r')

        #rewrapping coords into a Receiver instance
        receivers = Receiver()
        receivers.coord = file['coord'][:]
        
        output_data = {
            'receivers':receivers, 
            'freq' : file['freq'][:], 
            'p_mtx':file['p_mtx'][:],
            'fs': file['fs']
        }
        return output_data
    
    @staticmethod
    def read_hdf5(filename,path,autodict=True):
        """Lê um hdf5 vindo do export do colab

        Args:
            filename (_type_): _description_
            path (_type_): _description_

        Returns:
            _type_: um dict com os dados
        """
        file = h5py.File(f"{path}{filename}", 'r')

        if not autodict:
            output_data = {
                'pk':   file['pk'][:],
                'dir':  file['dir'][:],
                'freq': file['freq'][:],
                'k0':   file['k0'][:],
                'lambdavec': file['lambdavec'][:],
                'fs':   file['fs'][()],
            }
        else:
            # N vo nem fingir que n copiei do gepeto
            def extract_data(obj):
                data = {}
                for key, item in obj.items():
                    if isinstance(item, h5py.Group):
                        data[key] = extract_data(item)
                    elif isinstance(item, h5py.Dataset):
                        data[key] = item[:]
                return data
            output_data = extract_data(file)
        return output_data
