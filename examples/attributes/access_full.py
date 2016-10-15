class AttrDemo:
    """
    __getattr__ is only called if __getattribute is raising
    AttributeError or is specfically calling it.
    """
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __getattr__(self, item):
        print("never reached")

    def __getattribute__(self, item):
        print("access from getattribute")
        return item

assert "c" == AttrDemo(1, 2).c


class AttrDemo:

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __getattr__(self, item):
        print("access from getattr")
        assert item == "specific" or item == "exception"
        return -1

    def __getattribute__(self, item):
        print("access from getattribute")
        if item.startswith("exce"):
            raise AttributeError
        elif item.startswith("spec"):
            # in a strange way this calls __getattribute__ also...
            return self.__getattr__(item)

        return super().__getattribute__(item)


ad = AttrDemo(1, 2)
assert ad.a == 1
assert ad.b == 2

assert ad.specific == -1
assert ad.exception == -1
