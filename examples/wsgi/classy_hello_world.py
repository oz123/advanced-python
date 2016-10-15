class HelloWSGI:
    def __call__(self, environ, start_response):
        self.start_response('200 OK', [('Content-Type', 'text/plain')])
        yield b"Hello World!\n"

app = Application()


from wsgiref.simple_server import make_server
httpd = make_server('', 8000, app)
print("Serving on port 8000...")

# Serve until process is killed
httpd.serve_forever()
