import pprint
import functools as ft


def reverser(handler):

    # reverse all strings in response
    rev = lambda iterable: [x[::-1] for x in iterable]

    def _inner(environ, start_response):

        do_reverse = []

        # Override start_response to check the content type and set a flag
        def start_reverser(status, headers):
            for name, value in headers:
                if (name.lower() == 'content-type'
                        and value.lower() == 'text/plain'):
                    do_reverse.append(True)
                    break

            # Remember to call `start_response`
            start_response(status, headers)

        response = handler(environ, start_reverser)

        if do_reverse:
            return rev(response)

        return response

    return _inner


def app(environ, start_function):
    start_function('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]


def log_environ(handler):
    def _inner(environ, start_response):
        pprint.pprint(environ)
        return handler(environ, start_response)
    return _inner


# app = reverser(reverser(app))

# this is a list of middleware a la djangos list of middlewares.
MIDDLEWARES = [log_environ,
               reverser,
               reverser]

app = ft.reduce(lambda h, m: m(h), MIDDLEWARES, app)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
