class prop:
    def __init__(self, get_func):
        import pdb; pdb.set_trace()
        self.get_func = get_func

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return self.get_func(instance)

    def __set__(self, instance, value):
        self.set_func(instance, value)

    def setter(self, set_func):
        self.set_func = set_func
        return self

    def set_func(self, instance, value):
        raise TypeError("can't set me")

class Demo:
    _value = None

    @prop
    def readwrite(self):
        return self._value

    @readwrite.setter
    def readwrite(self, value):
        self._value = value

    @prop
    def readonly(self):
        return 133

obj = Demo()
print(obj.readwrite)
obj.readwrite = 'foo'
print(obj.readwrite)
print(obj.readonly)
obj.readonly = 'bar'  # TypeError!
