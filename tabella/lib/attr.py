class Attrs:

    def __init__(self, mapping):
        self.__dict__["_Attrs__mapping"] = mapping


    def __getattr__(self, name):
        try:
            return self.__mapping[name]
        except KeyError:
            raise AttributeError(name)


    def __setattr__(self, name, value):
        self.__mapping[name] = value


    def __delattr__(self, name):
        try:
            del self.__mapping[name]
        except KeyError:
            raise AttributeError(name)


    def __dir__(self):
        return tuple(self.__mapping.keys())



