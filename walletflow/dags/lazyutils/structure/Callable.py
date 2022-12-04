
class Callable:
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        self.run(*args, **kwargs)
