import pprint


def app(environ, start_function):
    start_function('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]


def log_environ(handler):
    def _inner(environ, start_fn):
        pprint.pprint(environ)
        return handler(environ, start_fn)
    return _inner


app = log_environ(app)

