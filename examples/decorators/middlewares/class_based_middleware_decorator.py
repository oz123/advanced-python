class CapitalizeResponse(object):

    def __init__(self, app):
        self.app = app
        self.visits = 0

    def __call__(self, environ, start_response, *args, **kwargs):
        self.visits += 1
        response = self.app(environ, start_response)
        response.append(("You visited " + str(self.visits) +
                         " times").encode())
        return [line.decode().upper().encode() for line in response]


@CapitalizeResponse
def handler(environ, start_function):
    start_function('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, handler)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
