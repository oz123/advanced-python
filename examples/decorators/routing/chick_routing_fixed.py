class Chick:

    """
    A WSGI Application frame with API inspired by Bottle and Flask.

    There is No HTTPRequest Object and No HTTPResponse object.

    Just barebone routing ...
    """

    routes = {}

    def __call__(self, environ, start_response):
        try:
            callback, method = self.routes.get(environ.get('PATH_INFO'))
        except TypeError:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'404 Not Found']

        if method != environ.get('REQUEST_METHOD'):
            start_response('405 Method Not Allowed',
                           [('Content-Type', 'text/plain')])
            return [b'404 Method Not Allowed']

        start_response('200 OK', [('Content-Type', 'text/plain')])
        return callback(environ)

    def add_route(self, path, wrapped, method):
        self.routes[path] = (wrapped, method)

    def get(self, path):
        def decorator(wrapped):
            self.add_route(path, wrapped, 'GET')
            return wrapped

        return decorator

    def post(self, path):
        def decorator(wrapped):
            self.add_route(path, wrapped, 'POST')
            return wrapped

        return decorator


chick = Chick()


@chick.get("/")
def index(environ):
    return [b"Hello World!\n"]


@chick.post("/input/")
def test_post(environ):

    r = ''.join(('{} {}\n'. format(k, v) for k, v in environ.items())).encode()
    return [r]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, chick)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
