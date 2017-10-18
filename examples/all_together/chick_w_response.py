"""
All together

Demonstrate how you can build a quick and dirty framework with a bottle like
API.

Chick is the main application frame.
CapitalizeResponse is a middleware which you can use to wrap your application.
It stores session information, and it capitalizes all responses.
"""


class Chick:

    """
    A WSGI Application framework with API inspired by Bottle and Flask.

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

        response = callback(environ)
        start_response(response.status, response.content_type)
        return response.body.encode()

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


class CapitalizeResponse:

    def __init__(self, app):
        self.app = app
        self.visits = 0  # state keeping made easier

    def __call__(self, environ, start_response, *args, **kw):
        self.visits += 1

        response = [self.app(environ, start_response)]

        response.append("\nYou visited {} times".format(self.visits).encode())

        return [line.upper()
                for line in response]


chick = Chick()


@chick.get("/")
def index(environ):
    return Response("hello world!")


@chick.post("/input/")
def test_post(environ):

    r = ''.join(('{} {}\n'. format(k, v) for k, v
                 in environ.items())).encode()
    return Response(r)


class Response:

    __slots__ = ('body', 'status', 'content_type')

    def __init__(self, body, status='200 OK',
                 content_type="text/plain"):
        self.body = body
        self.status = status
        self.content_type = [('Content-Type', content_type)]

    def __iter__(self):
        return [self.body]


@chick.get("/response/")
def response(environ):
    return Response("hello world!")


capital_chick = CapitalizeResponse(chick)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, capital_chick)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
