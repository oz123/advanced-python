def capitalize_response(handler):
    """dumb middleware the assumes response is a list of
       strings which can be capitlized"""

    def _inner(environ, start_response):
        response = handler(environ, start_response)
        return [line.decode().upper().encode() for line in response]

    return _inner


@capitalize_response
def handler(environ, start_function):
    start_function('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, handler)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
