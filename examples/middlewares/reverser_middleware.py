import time


def reverser(handler):

    def _inner(environ, start_response):
        response = handler(environ, start_response)
        new_response = [x[::-1] for x in response]
        print(new_response)
        return new_response

    return _inner


def app(environ, start_function):
    start_function('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]


# this will return Hello World
app = reverser(reverser(app))


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
