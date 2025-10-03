import os


_default_folder = os.path.expandvars('%userprofile%/Desktop')



class GlobalWorkspace:    
    global _default_folder
    default_folder = _default_folder

    @staticmethod
    def globalpath(path:(str)):
        global _default_folder

        _default_folder = os.path.expandvars(path)
        return _default_folder
    
    @staticmethod
    def file(filename:str) -> 'str':
        filepath = f'{GlobalWorkspace.default_folder}/{filename}'
        return filepath

