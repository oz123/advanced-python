import functools

def stylist(function=None, *, style='bold'):
    # based on http://stackoverflow.com/a/25827070/492620
    def actual_decorator(f):
        def wrapper(*args, **kwargs):
            if style == 'bold':
                return '**' + f(*args, **kwargs) + '**'
            if style == 'italic':
                return '__' + f(*args, **kwargs) + '__'
            else:
                f(*args, **args).upper()

        return wrapper
    if function:
        return actual_decorator(function)

    return actual_decorator


@stylist
def test1():
    return ('test1')


@stylist(style='italic')
def test2():
    return ('test2')

print(test1())
print(test2())


def stylist(func=None, *, style='bold'):
    # based on Python Cook book 3rd Ed.
    if func is None:
        return functools.partial(stylist, style=style)

    def wrapper(*args, **kwargs):
        if style == 'italic':
            return '__' + func(*args, **kwargs) + '__'
        if style == 'bold':
            return '**' + func(*args, **kwargs) + '**'
        else:
            return func(*args, **kwargs).upper()

    return wrapper

@stylist
def test3():
    return ('test3')


@stylist(style='bold')
def test4():
    return ('test4')


@stylist(style='italic')
def test5():
    return ('tes5')

print(test3())
print(test4())
print(test5())
