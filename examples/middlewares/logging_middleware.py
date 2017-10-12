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

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()

