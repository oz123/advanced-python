class AssignOnce:

    def __init__(self, initial_value, also_forbidden):

        self.forbidden = initial_value
        self.forbidden_too = also_forbidden

    def __setattr__(self, name, value):

        if name not in ['forbidden', 'forbidden_too']:
            pass
        elif name not in self.__dict__:
            pass
        else:
            raise AttributeError("Can't touch {}".format(name))

        super().__setattr__(name, value)

ao = AssignOnce(3, 1)

ao.somevalue = 4
print(ao.somevalue)
#  demonstrate we can access the values
print(ao.forbidden)
print(ao.forbidden_too)
# This will explode
try:
    ao.forbidden = 2
except AttributeError as E:
    print(E)

try:
    ao.forbidden_too = 4  # also explodes
except AttributeError as E:
    print(E)

# outputs:
# 4
# 3
# 1
# Can't touch forbidden
# Can't touch forbidden_too
