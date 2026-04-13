import os


_default_folder = os.path.expandvars('%userprofile%/Desktop')



class GlobalWorkspace:
    """
    Serve para criar um workspace folder fora do workspace folder basicamente, 
    sem precisar digitar paths complicados
    """    
    global _default_folder
    default_folder = _default_folder

    @staticmethod
    def globalpath(path:(str)) -> 'str':
        """Altera o caminho global do glws, caso o caminho não exista, a função tentará criar uma pasta no lugar

        Args:
            path (str): O novo caminho que a classe vai utilizar

        Returns:
            str: O novo caminho
        """
        global _default_folder
        if path[-1] == '/':
            path = path[:-1] 
        
        _default_folder = os.path.expandvars(path)
        # Cria uma pasta caso não exista
        os.makedirs(_default_folder,
                    exist_ok=True)
        return _default_folder
    
    @staticmethod
    def file(filename:str) -> 'str':
        """Retorna um caminho com o nome do arquivo ao final

        Args:
            filename (str): O nome do arquivo

        Returns:
            str: _description_
        """
        global _default_folder
        filepath = f'{_default_folder}/{filename}'
        return filepath
    

    @staticmethod
    def reset():
        global _default_folder
        
        _default_folder = os.path.expandvars('%userprofile%/Desktop')
        return _default_folder
    
class LocalWorkspace:    
    default_folder = _default_folder

    def __init__(self,path:str=''):        
        global _default_folder
        self.default_folder = _default_folder
        
        if not (path == ''):
            self.set_path(path)
    
    def set_path(self,path:(str)):
        if path[-1] == '/':
            path = path[:-1]

        self.default_folder = os.path.expandvars(path)
        
        os.makedirs(self.default_folder,
                    exist_ok=True)
    
    def file(self,filename:str) -> 'str':
        filepath = f'{self.default_folder}/{filename}'
        return filepath
