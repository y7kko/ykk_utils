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

    @classmethod
    def __getattr__(cls, name):
        return getattr(cls._references,name)

backend_collection = _backend_collection()
