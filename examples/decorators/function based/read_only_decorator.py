def read_only_properties(*attrs):

    def class_rebuilder(cls):

        class NewClass(cls):
            "This is the overwritten class"
            def __setattr__(self, name, value):
                if name not in attrs:
                    pass
                elif name not in self.__dict__:
                    pass
                else:
                    raise AttributeError("Can't touch {}".format(name))

                super().__setattr__(name, value)

        return NewClass

    return class_rebuilder


@read_only_properties('readonly', 'forbidden')
class MyClass(object):
    """
    This class is decorated
    """
    def __init__(self, a, b, c):
        self.readonly = a
        self.forbidden = b
        self.ok = c

    @property
    def area(self):
        return 4*12

m = MyClass(1, 2, 3)
print(m.ok, m.readonly)

# can touch ok
m.ok = 3
print("This worked...")
# this will explode
try:
    m.forbidden = 4
except AttributeError:
    pass

print(m.area)
