import threading


class Singleton(object):
    __instances = {}
    __lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls.__lock:  # If used with many threads, may impact on object creation performance
            if cls not in cls.__instances:
                cls.__instances[cls] = super(Singleton, cls).__new__(cls)
        return cls.__instances[cls]

    @classmethod
    def reset(cls):
        """
        Reset class instance from internal control, but you should rebuild again, so garbage collector can dispose
        current instance. \n
        \n
        foo = Foo() \n
        foo.reset() \n
        foo = Foo() #If not, you are going to keep using the same memory instance \n

        """

        with cls.__lock:
            cls.__instances.pop(cls)
