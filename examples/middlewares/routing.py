def not_found(environ, start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'404 Not Found']


def hello_world(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]

def greet_user(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    user = environ.get('USER')
    return ["Welcome {}!\n".format(user).encode()] # response must contain bytes


def app(environ, start_response):
    handler = URLS.get(environ.get('PATH_INFO')) or not_found
    return handler(environ, start_response)


URLS = {
    "/": hello_world,
    "/greeter": greet_user,
}

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, app)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
