import h5py
import warnings
from receivers import Receiver
try:
    import pyperclip
except:
    pass

class colabrw():
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

    def cloud_read(filename,path):
        file = h5py.File(f"{path}{filename}", 'r')

        #rewrapping coords into a Receiver instance
        receivers = Receiver()
        receivers.coord = file['coord'][:]
        
        output_data = {
            'receivers':receivers, 
            'freq' : file['freq'][:], 
            'p_mtx':file['p_mtx'][:]
        }
        return output_data
