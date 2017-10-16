def bump(argument):
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            return argument + function(*args, **kwargs)
        return wrapper
    return real_decorator


@bump(7)
def add(a, b):
    return a+b


assert add(3, 10) == 20



