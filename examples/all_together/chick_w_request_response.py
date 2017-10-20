"""
All together

Demonstrate how you can build a quick and dirty framework with a bottle like
API.

Chick is the main application frame.
CapitalizeResponse is a middleware which you can use to wrap your application.
It stores session information, and it capitalizes all responses.
"""


def request_factory(env):
    """
    Dynamically create a Request class with slots and read
    only attributes

    """
    class Request:

        __slots__ = [k.replace(".", "_").lower() for k in env.keys()]

        def __setattr__(self, name, value):
            try:
                getattr(self, name)
                raise ValueError("Can't modify {}".format(name))
            except AttributeError:
                super().__setattr__(name, value)

    request = Request()

    for k, v in env.items():
        setattr(request, k.replace(".", "_").lower(), v)

    return request


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

        request = request_factory(environ)
        response = callback(request)

        start_response(response.status, response.content_type)
        return (response.body.encode(),)

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


class Response:

    __slots__ = ('body', 'status', 'content_type')

    def __init__(self, body, status='200 OK',
                 content_type="text/plain"):
        self.body = body
        self.status = status
        self.content_type = [('Content-Type', content_type)]

    def __iter__(self):
        return [self.body]


class CapitalizeResponseMiddleware:

    """
    A middlerware that manipulates the response
    """
    def __init__(self, app):
        self.app = app
        self.visits = 0  # state keeping made easier

    def __call__(self, environ, start_response, *args, **kw):
        self.visits += 1

        response = self.app(environ, start_response)
        response = [line.upper() for line in response]
        response.append("\nYou visited {} times".format(self.visits).encode())

        return response


chick = Chick()


@chick.get("/")
def index(request):
    return Response("hello world!")


@chick.post("/input/")
def test_post(request):

    return Response("")


@chick.get("/response/")
def response(request):

    res = "".join("{}: {}\n".format(s, getattr(request, s))
                  for s in request.__slots__)

    return Response("hello world!\n" + res)


capital_chick = CapitalizeResponseMiddleware(chick)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, capital_chick)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
