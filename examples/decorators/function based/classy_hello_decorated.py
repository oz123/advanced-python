from wsgiref.simple_server import make_server


def capitalize(cls):

    class NewClass(cls):

        def __call__(self, *args, **kwargs):
            response = super().__call__(*args, **kwargs)
            return [line.decode().upper().encode() for line in response]

    return NewClass


@capitalize
class HelloWSGI:

    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        yield b"Hello World!\n"

hello_world = HelloWSGI()


httpd = make_server('', 8000, hello_world)
print("Serving on port 8000...")

# Serve until process is killed
httpd.serve_forever()
