import random

def capitalize(cls):
    old_call = cls.__call__

    def __newcall__(self, *args, **kwargs):
        value = old_call(self)
        return value.upper()

    cls.__call__ = __newcall__
    return cls


def all_caps(cls):

    class NewClass(cls):

        def __call__(self, *args, **kwargs):
            value = super().__call__()
            return value.upper()

    return NewClass



def make_style_function(style):
    if style == "bold":
        stylist = lambda x: "**" + x + "**"
    elif style == "upper":
        stylist = lambda x: x.upper()
    elif style == "italic":
        stylist = lambda x: "__" + x + "__"
    else:
        raise ValueError("Unknown style")

    return stylist


def stylist(*args, **kwargs):
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        style = random.choice(["bold", "upper", "italic"])
        stylist = make_style_function(style)

        cls = args[0]

        class NewClass(cls):

            def __call__(self, *args, **kwargs):
                return stylist(super().__call__())

        return NewClass
    else:
        style = args[0]
        stylist = make_style_function(style)

        def class_builder(cls):
            class NewClass(cls):

                def __call__(self, *args, **kwargs):
                    return stylist(super().__call__())

            return NewClass

        return class_builder


@capitalize
class Hello:
    def __init__(self, a):
        self.a = a

    def __call__(self):
        return self.a


@all_caps
class HelloAgain:
    def __init__(self, a):
        self.a = a

    def __call__(self):
        return self.a


@stylist("upper")
@stylist("bold")
class HelloWithStyle:
    def __init__(self, a):
        self.a = a
    def __call__(self):
        return self.a

@stylist
class HelloAgainWithStyle:
    def __init__(self, a):
        self.a = a
    def __call__(self):
        return self.a

hl = Hello("hello")
hl2 = HelloAgain("hello")
hl3 = HelloWithStyle("hello")
hl4 = HelloAgainWithStyle("hello")
print(hl3())
print(hl4())
