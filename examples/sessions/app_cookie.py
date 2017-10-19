from http.cookies import SimpleCookie

def reverser(handler):

    def _inner(environ, start_response):
        response = handler(environ, start_response)
        new_response = [x[::-1] for x in response]
        print(new_response)
        return new_response

    return _inner


def app(environ, start_function):
    start_function('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n", b"HFOO"]


class Middleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):

        def custom_start_response(status, headers, exc_info=None):
            headers.append(('Set-Cookie', "name=value"))
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response) + [b"\nbla "]


# this will return Hello World
app = Middleware(reverser(reverser(app)))


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
