class Chick:

    routes = {}

    def __call__(self, environ, start_response):
        callback = self.routes.get(environ.get('PATH_INFO'))
        if not callback:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'404 Not Found']
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return callback(environ)

    def add_route(self, path, wrapped):
        self.routes[path] = wrapped

    def get(self, path):
        def decorator(wrapped):
            self.add_route(path, wrapped)
            return wrapped

        return decorator


chick = Chick()


@chick.get("/")
def index(environ):
    return [b"Hello World!\n"]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, chick)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
