
class Demo:
    a = 1
    b = 2

    def __init__(self, a):
        self.a = a

    def __getattr__(self, item):
        print("item accessed from here: {}".format(item))
        return "c"

demo = Demo("instance attribute")

assert demo.a != 1
assert demo.b == 2
assert demo.c == "c"

demo.c = 3

assert demo.c == 3
