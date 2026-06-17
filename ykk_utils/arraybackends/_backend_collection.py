class _backend_collection:
    _references = {}

    @classmethod
    def __getitem__(cls, key):
        """Permite usar _BackendCollection['numpy']"""
        return cls._references[key]
    
    @classmethod
    def __setitem__(cls, key, value):
        """Permite usar _BackendCollection['numpy'] = backend"""
        cls._references[key] = value

backend_collection = _backend_collection()
