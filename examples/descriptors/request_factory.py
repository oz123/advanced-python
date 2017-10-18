def request_factory(env):
    """
    Dynamically create a Request class with slots and read
    only attributes

    """
    class Request:
        __slots__ = env.keys()

        def __setattr__(self, name, value):
            try:
                getattr(self, name)
                raise ValueError("Can't modify {}".format(name))
            except AttributeError:
                super().__setattr__(name, value)
    request = Request()
    for k, v in env.items():
        setattr(request, k, v)
    return request


r = request_factory({"foo": "bar"})
