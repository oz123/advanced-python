"""
example from http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/
Ported to Python3
"""

import re
from cgi import escape


def index(environ, start_response):
    """This function will be mounted on "/" and display a link
    to the hello world page."""
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b'''Hello World Application
               This is the Hello World application:

`continue <hello/>`_

''']


def hello(environ, start_response):
    """Like the example above, but it uses the name specified in the
URL."""
    # get the name from the url if it was specified there.
    args = environ['myapp.url_args']
    if args:
        subject = escape(args[0])
    else:
        subject = 'World'
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''Hello {}!'''.format(subject).encode()]


def not_found(environ, start_response):
    """Called if no URL matches."""
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return [b'Not Found']


def test(environ, start_response):
    """Like the example above, but it uses the name specified in the
URL."""
    # get the name from the url if it was specified there.
    args = environ['myapp.url_args']
    if args:
        args = ",".join(escape(a) for a in args)
    else:
        args = 'No Args'
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''Args: {}!'''.format(args).encode()]


# map urls to functions
urls = [
    (r'^$', index),
    (r'hello/?$', hello),
    (r'hello/(.+)$', hello),
    (r'test/(.+)/(\d+)$', test)
]


def application(environ, start_response):
    """
    The main WSGI application. Dispatch the current request to
    the functions from above and store the regular expression
    captures in the WSGI environment as  `myapp.url_args` so that
    the functions from above can access the url placeholders.

    If nothing matches call the `not_found` function.
    """
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match:
            environ['myapp.url_args'] = match.groups()
            return callback(environ, start_response)

    return not_found(environ, start_response)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")

    # Serve until process is killed
    httpd.serve_forever()
