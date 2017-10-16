class cached_property:
    """A property that is only computed once per instance and
    then replaces itself with an ordinary attribute.
    Deleting the attribute resets the property."""

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def fibonnaci(end):
    if end == 0:
        return 1
    if end == 1:
        return 1
    else:
        return fibonnaci(end-2) + fibonnaci(end-1)


env = {"dont": "touch me", "wont": "allow this"}


class Request:

    read_only = ['dont', 'wont']

    def __init__(self, environ):
        self.n = 12
        self.from_env(environ)

    def __setattr__(self, name, value):
        if name not in Request.read_only:
            pass
        elif name not in self.__dict__:
            pass
        else:
            raise AttributeError("Can't touch {}".format(name))

        super().__setattr__(name, value)

    def from_env(self, env):
        for k, v in env.items():
            setattr(self, k, v)

    @cached_property
    def fib(self):
        return fibonnaci(self.n)

    @cached_property
    def url(self):
        return self.dont + " " + self.wont


f = Request(env)
a = f.fib
a = f.fib

# this is allowed
f.n = 2
print(f.fib)
print(f.url)

f.dont = 'blows up'
