class Singleton(object):
    __instances = {}

    # def __call__(cls, *args, **kwargs):
    #     if cls not in cls._instances:
    #         cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    #     return cls._instances[cls]

    def __new__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__new__(cls)
        return cls.__instances[cls]

    @classmethod
    def _reset(cls):
        cls.__instances.pop(cls)

    def reset(self):
        """
        Reset class instance from internal control, but you should rebuild again, so garbage collector can dispose
        of current instance. \n
        \n
        foo = Foo() \n
        foo.reset() \n
        foo = Foo() #If not, you are going to keep using the same memory instance \n

        """
        pass
