class cached_property:
  """A property that is only computed once per instance and
  then replaces itself with an ordinary attribute.
  Deleting the attribute resets the property."""

  def __init__(self, func):
    self.__doc__ = getattr(func, '__doc__')
    self.func = func

  def __get__(self, obj, cls):
    if obj is None: return self
    value = obj.__dict__[self.func.__name__] = self.func(obj)
    return value


def fibonnaci(end):
    if end == 0: return 1
    if end == 1: return 1
    else: return fibonnaci(end-2) + fibonnaci(end-1)

class Foo:

    def __init__(self, n):
        self.n = n

    @cached_property
    def fib(self):
        return fibonnaci(self.n)

f = Foo(12)
a = f.fib
a = f.fib

