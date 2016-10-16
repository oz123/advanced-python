name: inverse
layout: true
class: center, middle, inverse

---

# Advanced Web Programming with Python
## Plone Conf, Boston
### Oz Tiram, 17 October 2016
---

# About this course
???

 In this course you will learn a few subjects  concerning Python web
 Development.
 We will start by exploring WSGI, Python protocol for connecting
 Python applications to Web Servers.
 We will then build a simple blogging application through which we will
 explore some patterns and anti-patterns for making a Python web app.
 We shall talk about testing, securing our application, our deploying.
 We also explore some more advanced Python topics which might not be
 familiar to Python beginners and maybe even People with several years
 of experience in Python.

---
class: center, middle, inverse
# Part 1 - Web frameworks demystified
---
class: center, middle, inverse
## WSGI Compliant Python Web Frameworks

![-resize-50](./static/wsgi-fw.png)

---
## Web Server Gateway Interface

???

 In the past, before WSGI, developers who wanted to create a web application
 with Python had to choose between different frameworks and webservers.
 Python applications were often designed for only one of CGI,
 FastCGI, mod_python or some other custom API of a specific web server.
 This wide variety of choices can be a problem for new Python users,
 because generally speaking, their choice of web framework limited
 their choice of usable web servers, and vice versa.

 WSGI was created as a low-level interface between web servers and
 web applications or  frameworks to promote a common ground for
 portable web application development. This is similar to Java's
 "servlet" API makes it possible for applications written with any
 Java web application framework to run in any web server that
 supports the servlet API. [pep-333]


 https://www.fullstackpython.com/wsgi-servers.html
---
class: center, inverse
# From the Browser to Python and back
![](./static/http-server-app.svg)
---
# WSGI Servers

![](./static/wsgi-servers.svg)

---
layout: false
class: left
# Hello World in WSGI

```python
def hello_world_app(environ, start_response):
    status = '200 OK'  # HTTP Status
    # HTTP Headers
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)

    # The returned object is going to be printed
    return [b"Hello World"]
```

 - `start_response` is given by the server. You just call it.
???

 A wsgi application is just a callable object the respods to
 requests but taking two arguments.
 The first one being the `environment` and the second being
 `start_response`.
 The environment is a Python dictionary containing information
 about the  CGI environment, with keys like REQUEST_METHOD, HTTP_HOST, etc.
 `start_response `is a callback function that an application
 invokes to return status and header information to the calling software.
 The start_response callback takes two inputs:
 `status` and `headers`, `status` is a string representation of an
 HTTP status, such as `200 OK`. `headers`  is a list of two-value tuples,
 of possible HTTP headers.
 The `start_response` callable must return a `write(body_data)` callable
 `start_response` is implemented by the
  WSGI server and not by the Python Web Framework.

  When called by the server,
  the application object must return an iterable yielding
  zero or more strings. This can be accomplished in a variety of ways.

---
# Invoking your WSGI application

### For testing purposes you can use the built-in server from the standard library

```python
from wsgiref.simple_server import make_server

def hello_world_app(environ, start_response):
    status = '200 OK'  # HTTP Status
    # HTTP Headers
    headers = [('Content-type', 'text/plain; charset=utf-8')]
    start_response(status, headers)

    # The returned object is going to be printed
    return [b"Hello World"]

httpd = make_server('', 8000, app)
print("Serving on port 8000...")
# Serve until process is killed
httpd.serve_forever()
```
???
see examples/wsgi/hello_world.py
---
# Can you write a WSGI app with a class?

 * a callable which takes:
  - `environ`
  - `start_response`
 * return a response

---
# A classy WSGI app

```
class HelloWSGI:

    def __call__(self, environ, start_response):
        self.start_response('200 OK', [('Content-Type', 'text/plain')])
        yield b"Hello World!\n"

hello_world = Application()
```
???
see examples/wsgi/classy_hello_world.py

---
# Middlewares

 * Middleware are wrappers around your application
 * They can manipulate your app's response
 * The can route a request to different callable objects
???
 A middleware is an object that wrapps the original application,
 hence the name. A middle is called between the application and the server.
 It can modify the response or the environment or route requests to
 different application objects.

 URL dispatching
 http://pythonpaste.org/modules/urlmap.html#module-paste.urlmap
 http://pythonpaste.org/url-parsing-with-wsgi.html
---
# Middlewares in Work

![-resize-50](./static/middlewares2.png)

---
# Example
```python

def log_environ(handler):
    """print the envrionment dictionary to the console"""
    from pprint import pprint
    def _inner(environ, start_function):
        pprint(environ)
        return handler(environ, start_function)
    return _inner

# this will show "Hello World!" in your browser,
# and the environment in the console
app = log_environ(hello_world_app)
```
???

see examples/middlewares/logging_middleware.py

---
# Plumbing Middlewares

```shell
$ pip install django
$ django-admin startproject example
$ grep -C2 -ni  middleware example/example/settings.py
```

???
 Middlewares and apps are agnostic to each other,
 so we can plumb any WSGI app to our middleware,
 and our middleware to any WSGI app. Middleware can be chained,
 allowing our response or request to go through mulitple
 phases of processing.

---
# Plumbing Middlewares

```shell
$ pip install django
$ django-admin startproject example
$ grep -C2 -ni  middleware example/example/settings.py
40-]
41-
42:MIDDLEWARE = [
43:    'django.middleware.security.SecurityMiddleware',
44:    'django.contrib.sessions.middleware.SessionMiddleware',
45:    'django.middleware.common.CommonMiddleware',
46:    'django.middleware.csrf.CsrfViewMiddleware',
47:    'django.contrib.auth.middleware.AuthenticationMiddleware',
48:    'django.contrib.messages.middleware.MessageMiddleware',
49:    'django.middleware.clickjacking.XFrameOptionsMiddleware',
50-]
51-
```
???
So basically, Dajngo imports these middlewares from the their
specified module and plumbs them one after another. Let's see how
we can do that too.

---
# Plumbing middlewares example

```
def reverser(handler):

    def _inner(environ, start_response):
        response = handler(environ, start_response)
        new_response = [x[::-1] for x in response]
        print(new_response)
        return new_response

    return _inner

# this will return the original Hello World!
app = reverser(reverser(app))
```
???

see
 examples/middlewares/cappitalize_middleware.py
 examples/middlewares/reverser_middleware.py
 examples/middlewares/plumbing_middlewares.py
---
# Routing of URLs

 * map a url to a callable

```python
# flask, bottle style routing
@app.route("/")
def hello():
    return "Hello World!"
```

### Can you implement a simple routing middleware?

???
You can implement complex routing parsers, but basically it boils down
to a lookup of the request's `PATH_INFO` to some callable.

Later on in the course we will talk about decorators, and implement a `get`
decorator for routing.
---
# A very simple example of routing

```python
def not_found(environ, start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'404 Not Found']

def greet_user(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    user = environ.get('USER')
    return ["Welcome {}!\n".format(user).encode()] # response must contain bytes


URLS = {
    "/": hello_world,
    "/greeter": greet_user,
}

def app(environ, start_response):
    handler = URLS.get(environ.get('PATH_INFO')) or not_found
    return handler(environ, start_response)

```
???
This is simple lookup and mapping of a URL to an appropriate response.
And with this we have learned the basics of how a WSGI application works.
But there is a still long way from this basic WSGI app to a modern
Python web framework.

see

 examples/middlewares/routing.py

---
# From raw WSGI to a web framework

 * pre-process the `environment`
   - yield a `request` object to work with
 * route `PATH_INFO` to your views
 * add session management
 * ship some common middlewares and classes to create valid HTTP responses
 * add some HTML templating
 * Optionally give you some data storage layer

---
# Cookies and Sessions

 * Cookies are a mechanism to manage state in HTTP (which is stateless)
  - Python STL `http.cookies`
 * Sessions are a mechanism  to persist the user's interaction with the website.
  - Sessions rely on reading a unique session id from information stored in
  the browser.

???

http://www.lassosoft.com/Tutorial-Understanding-Cookies-and-Sessions
---
# Session middelware

 * Wrap our application with a middleware that stores information
 * We don't know how the data is structured
 - We need some kind of a key value store:

```
 sessions = {
    "id1": {'data': {'k1': 'v1', 'k2': 'v2', ..., 'kn': 'vn'}},
    "id2": {'data': {'ka1': 'va1', 'ka2': 'va2', ..., 'kan': 'van'}},
    ... }

```

---
class: center, middle, inverse
# Part 2 - Python's Data Model

---
# A dive into Python's Data Model

 * Understanding **magic** or `__dunder__` methods
 * Customize assignment and retrieval of properties

???

Understanding how objects work in Python, will help us create an Object that
we can assign items to, having the items saved as keys, and the attributes
as the data entry.

The first thing to know about special methods is that they are menato to be
called by the Python interpreter, and not by you [Fluent Python, pg. 8].

---
# Attribute access

## Class access
```
Item.x -> Item.__dict__['x']
```
## Instance attribute access (approximately)

### with `__getattr__` only, later we will see the full process ...

```
Item(x) -> item.x -> item.__dict__['x'] ?
    Item.__dict__['x'] ? Item.__getattr__('x')
```

### Exercise: create a class and instance that demonstrate the above sequence.

???

This all first counts for a class.
Instance access is a bit different,

A class instance is created by calling a class object (see above).

A class instance's `_dict__` is the first place in which attribute references
are searched. When an attribute is not found there, and the instance's class
has an attribute by that name, the search continues with the class attributes.
If no class attribute is found, and the object's class has a `__getattr__()`
method, that is called to satisfy the lookup.

but that's not it. You can customize the access!

Attribute assignments and deletions update the instance's dictionary,
never a class's dictionary. If the class has a `__setattr__()` or
`__delattr__()` method, this is called instead of updating the instance
dictionary directly.

Class instances can pretend to be numbers, sequences, or mappings if they
have methods with certain special names. See section Special method names.

---
Attribute Access demo:

```
class Demo:
    a = 1
    b = 2

    def __init__(self, a):
        self.a = a

    def __getattr__(self, item):
        print("item accessed from here: {}".format(item)
        return "c"

demo = Demo("instance attribute")

assert demo.a != 1
assert demo.b == 2
assert demo.c == "c"
demo.c = 3
assert demo.c == 3
```
???
see examples/attributes/access.py

---
## Customizing assignment with `__setattr__`

 * `__setattr__` is called instead of
   updating `item.__dict__` directly

---
## Customizing assignment, example
```
from datetime import datetime as dt
class RevController:
    "records all mutations to disk"

    def __setattr__(self, name, value):
        with open("RevController.txt", "a+") as f:
            f.write("{} {} {}\n".format(dt.utcnow(),
                                        name, value))
        super().__setattr__(name, value)

rc = RevController()

rc.a = 1
print(rc.a)
rc.a = 2
print(rc.a)
```
---
## Exercise: create a class with Read Only attributes
```
class AssignOnce:

   def __init__(self, initial_value):
       self.forbidden = initial_value

   def __setattr__(self, name, value):
       ...

fw = AssignOnce(2)
fw.ok = 3
# trying to re-assign forbidden, should raise AttributeError
fw.forbidden = 3
```
???

Hint: Create Read only attributes

see examples/attributes/read_only.py
see examples/attributes/rev_controller.py

---
### Solution

```python
class AssignOnce:

    def __init__(self, initial_value, also_forbidden):

        self.forbidden = initial_value
        self.forbidden_too = also_forbidden

    def __setattr__(self, name, value):

        if name not in ['forbidden', 'forbidden_too']:
            pass
        elif name not in self.__dict__:
            pass
        else:
            raise AttributeError("Can't touch {}".format(name))

        super().__setattr__(name, value)
```
---
### Customizing assignment with `__setitem__`

Dictionary style assignment with

`item[key] = val`

### Customizing retrieval with `__getitem__`

`val = item[key]`
---
# A dictionary like object Example
```
class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def __repr__(self):
        return "Point(%s, %s)" % (self.x, self.y)
    def __getitem__(self,item):
        return self.__dict__[item]
    def __setitem__(self, item, value):
        self.__dict__[item] = value

>>> p = Point(1,1)
>>> p
Point(1,1)
p['x'], p['y'] = 2, 5
>>> p['x'], p['y']
(2, 5)
```
---
## Slicing
### assign, retreive and delete chunks of list like objects
```
def __getitem__(self, key):
    if isinstance(key, slice):
        return [self.list[i] for i in range(key.start, key.stop, key.step)]
    return self.list[key]
```
## Checking membership
```
    def __contains__(self, id):
        """check if id in self"""
        if id in self.sessions:
            return True
        else:
            return False
```
---
## Instance attribute access - a completer view with `__getattribute__`

```
item.x -> item.__getattribute__('x') ? AttributeError ->
    Item.__getattr__('x')
```
???

http://stackoverflow.com/questions/4295678/understanding-the-difference\
 -between-getattr-and-getattribute
http://stackoverflow.com/questions/3278077/difference-between\
-getattr-vs-getattribute


__getattrbute__ Called unconditionally to implement attribute accesses for
instances of the class.
If the class also defines __getattr__(), the latter will not be called
unless __getattribute__() either calls it explicitly or
raises an AttributeError. This method should return the (computed)
attribute value or raise an AttributeError exception.
In order to avoid infinite recursion in this method, its implementation
should always call the base class method with the same name to access any
attributes it needs, for example, object.__getattribute__(self, name).

---
## `__getattribute__` is tricky ...

```
class AttrDemo:
    def __init__(self, a, b):
        self.a = a
    def __getattr__(self, item):
        assert item == "specific" or item == "exception"
        return item
    def __getattribute__(self, item):
        if item.startswith("exce"):
            raise AttributeError
        elif item.startswith("spec"):
            return self.__getattr__(item)
        return super().__getattribute__(item)

ad = AttrDemo(1, 2)
ad.a == 1

assert ad.specific == 'specific'
assert ad.exception == 'exception'
```
???

see examples/attributes/access_full.py

---
# Task: Create a session middleware with the following attributes:

 * Use cookies to remember the user
 * No disk persistence
 * Dictionary like access to attributes

---
class: remark-small-code
```
# in Session and DictBasedSessionManager  __contains__, __setitem__, __getitem__
class SimpleSessionMiddleware(object):
    def __init__(self, app, session_manager=DictBasedSessionManager,
                 env_key='wsgisession', cookie_key='session_id'):
        self.app = app
        self.env_key = env_key
        self.cookie_key = cookie_key
        self.manager = session_manager # missing

    def __call__(self, environ, start_response):
        cookie = SimpleCookie()
        if 'HTTP_COOKIE' in environ:
            cookie.load(environ['HTTP_COOKIE'])
        id = None
        if self.cookie_key in cookie:
            id = cookie[self.cookie_key].value
        session = SimpleSession(self.manager) # missing
        session.load(id)
        environ[self.env_key] = session

        def middleware_start_response(status, response_headers, exc_info=None):
            session = environ[self.env_key]
            session.save() # missing
            cookie = SimpleCookie()
            cookie[self.cookie_key] = session.id
            cookie[self.cookie_key]['path'] = '/'
            cookie_string = cookie[self.cookie_key].OutputString()
            response_headers.append(('Set-Cookie', cookie_string))
            return start_response(status, response_headers, exc_info)
        return self.app(environ, middleware_start_response)
```
???


My Solution to the session problem:
https://github.com/oz123/WSGISession

---
## `__slots__`

 * Speed up attribute access
 * Save memory (instances are created without `__dict__`)
 * Don't come for free
  - mess up with multiple inheritance
  - read only class attributes
  - prevent dynamic assignment of attributes not previously declared
???

https://docs.python.org/2/reference/datamodel.html#implementing-descriptors
By default, instances of both old and new-style classes have a dictionary
for attribute storage.
This wastes space for objects having very few instance variables.
The space consumption can become acute when creating large numbers of instances.

The default can be overridden by defining __slots__ in a new-style class
definition.
The __slots__ declaration takes a sequence of instance variables and reserves
just enough space in each instance to hold a value for each variable.
Space is saved because __dict__ is not created for each instance.
---
## `__slots__` example
```
class Session:
    __slots__ = ('id', 'data')

session = Session()
session.id = 'aef9136cebs2' # OK
session.cookie = SimpleCookie() # Not OK
# AttributeError: 'Session' object has no attribute 'cookie'
```

???
https://github.com/oz123/WSGISession/blob/descriptors_for_type_checking/wsgisession.py
https://github.com/oz123/WSGISession/blob/descriptors_for_type_checking/wsgisession.py#L87
---
# Descriptors:

### Objects that implement `__get__`, `__set__`, and `__del__`
### Can be used for typing, data verification, lazy retrieval or even caching.
### Data descriptors vs. non Data descriptors
 - descriptors are put in the class level (not in the instance)
???

If an object defines both __get__() and __set__(), it is considered a data
descriptor. Descriptors that only define __get__() are called non-data
descriptors (they are typically used for methods but other uses are possible).

http://intermediatepythonista.com/classes-and-objects-ii-descriptors
---
## Descriptors, example with SessionId
```python
class SessionId:

    def __get__(self, obj, objtype):
        return self.key

    def __set__(self, s_obj, s_key):
        if not set(s_key).issubset(set(string.ascii_lowercase + string.digits)):
            raise ValueError("Invalid characters in session key")
            setattr(s_obj, "id", s_key)
        self.key = s_key

class SessionIdChecked(BaseSessionMixin):

    id = SessionId()

    def __init__(self):
        self.data = {}
```
---
# Descriptors, stuff to remember

 - descriptors are invoked by the `__getattribute__()` method
 - overriding `__getattribute__()` prevents automatic descriptor calls
 - `object.__getattribute__()` and `type.__getattribute__()`
   make different calls to `__get__()`.
 - data descriptors always override instance dictionaries.
 - non-data descriptors may be overridden by instance dictionaries.
 - not always easy to combine with `__slots__`

---
# cached properties

```
class cached_property:
  """A property that is only computed once per instance and
  then replaces itself with an ordinary attribute.
  Deleting the attribute resets the property."""

  def __init__(self, func):
    self.__doc__ = getattr(func, '__doc__')
    self.func = func

  def __get__(self, obj, cls):
    if obj is None: return self
    value = obj.__dict__[self.func.__name__] = self.func(obj)
    return value
```

---
### cached properties, usage example
```
def fibonnaci(end):
    if end == 0: return 1
    if end == 1: return 1
    else: return fibonnaci(end-2) + fibonnaci(end-1)

class Foo:

    def __init__(self, n):
        self.n = n

    @cached_property
    def fib(self):
        return fibonnaci(self.n)

f = Foo(12)
a = f.fib
a = f.fib
```
???

Please run this code in your interactive session
It is, in Python parlance, a non-data descriptor.
In `pyramid` `cached_property` is called `@reify`

see:

  examples/descriptors/cached_property.py

---
# Decorators are ...

 - closures
 - syntactic sugar
 - confusing?

???
Closure is a fancy term meaning that when a function is declared, it maintains
a reference to the lexical environment in which it was declared.
http://www.brianholdefehr.com/decorators-and-functional-python

good explanation of what is going on
http://www.brianholdefehr.com/decorators-and-functional-python

Reading materail about decorators

https://github.com/GrahamDumpleton/wrapt/tree/master/blog

---
## closures

```
def reverser(app):
    # reverse all strings in response
    rev = lambda iterable: [x[::-1] for x in iterable]
    def _inner(environ, start_response):
        do_reverse = []
        def start_reverser(status, headers):
            for name, value in headers:
                if (name.lower() == 'content-type'
                        and value.lower() == 'text/plain'):
                    do_reverse.append(True)
                    break
            start_response(status, headers)
        response = handler(environ, start_reverser)
        if do_reverse:
            return rev(response)

        return response
    return _inner
```
???
Try running the same code when do_reverse is a boolean and not a list

This is because of how Python it manages the functions variable scope.
While the inner function can read the outer function's variables,
it cannot write them.

In some languages, the variable bindings contained in a closure behave
just like any other variables. Alas, in python they are read-only.
This is similar to Java, and has the same solution: closing container objects.
Closure of a dictionary or array won't let you assign a new dictionary or array,
but will let you change the contents of the container.
This is a common use pattern - every time you set a variable on self,
you are changing the contents of a closed dictionary.

http://ynniv.com/blog/2007/08/closures-in-python.html

---
# Syntactic sugar

```
# instead of
# app = capitalize_response(handler)
# we can do this

@capitalize_response
def handler(environ, start_function):
    start_function('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    # no longer needed
    # httpd = make_server('', 8000, app)
    httpd = make_server('', 8000, handler)
    print("Serving on port 8000...")
```
---
# Decorators are a
## ~~function that wraps a function~~
## a *callable* that wraps a *callable*

???
---
# Class based decorators

```
class CapitalizeResponse(object):
    def __init__(self, app):
        self.app = app
        self.visits = 0  # state keeping made easier
    def __call__(self, environ, start_response, *args, **kw):
        self.visits += 1
        response = self.app(environ, start_response)
        response.append(("You visited " + str(self.visits) +
                         " times").encode())
        return [line.decode().upper().encode()
                for line in response]
@CapitalizeResponse
def handler(environ, start_func):
    start_func('200 OK', [('Content-Type', 'text/plain')])
    return [b"Hello World!\n"]
```

???
see examples/middlewares/class_based_middleware_decorator.py

---
# Class decorators

 - take a class a parameter and patch it
 - can take action before the actual class is called
 - return the modified class

---
### function based class decorators, example

```python
def capitalize(cls):

    class NewClass(cls):

        def __call__(self, *args, **kwargs):
            response = super().__call__(*args, **kwargs)
            return [line.decode().upper().encode()
                    for line in response]

    return NewClass


@capitalize
class HelloWSGI:

    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type',
                                   'text/plain')])
        yield b"Hello World!\n"
```
???
raise your hand if you think or though, this is stupid, that is why
we have inheritance for modifying classes ...
---
### function based class decorators, with parameters
```
def stylist(style):
    if style == "bold":
        stylist = lambda x: "**" + x + "**"
    elif style == "upper": stylist = lambda x: x.upper()

    def class_builder(cls):
        class NewClass(cls):
            def __call__(self, *args, **kwargs):
                return stylist(super().__call__())
        return NewClass
    return class_builder

@stylist("upper")
@stylist("bold")
class HelloWithStyle:
    def __init__(self, msg):
        self.msg = msg
    def __call__(self):
        return self.msg
```

---
# class based class decorators

 - Implement a class decorator which makes all attributes read only
 - Hint: the modified class overrides both `__getattr__` and `__setattr__`

---
# Decorators with (optional) arguments
```
@decorator(a, b)
def function(x, y):
    pass


# evaluates to
def function(a, b)
    pass

function = decorator(a, b)(function)
```
???

http://stackoverflow.com/a/25827070/492620
http://scottlobdell.me/2015/04/decorators-arguments-python/
# good example
http://stackoverflow.com/a/653478/492620

Keyword only syntax.
https://www.python.org/dev/peps/pep-3102/
---
# Decorators with arguments
```
def stylist(function=None, *, style='bold'):
    # based on http://stackoverflow.com/a/25827070/492620
    def actual_decorator(f):
        def wrapper(*args, **kwargs):
            if style == 'bold':
                return '**' + f(*args, **kwargs) + '**'
            if style == 'italic':
                return '__' + f(*args, **kwargs) + '__'
            else:
                f(*args, **args).upper()

        return wrapper
    if function:
        return actual_decorator(function)

    return actual_decorator
```
???
see examples/middlewares/decorator_with_args.py
---
# Decorators with arguments
```
import functools

def stylist(func=None, *, style='bold'):
    if func is None:
        return functools.partial(stylist, style=style)

    def wrapper(*args, **kwargs):
        if style == 'italic':
            return '__' + func(*args, **kwargs) + '__'
        if style == 'bold':
            return '**' + func(*args, **kwargs) + '**'
        else:
            return func(*args, **kwargs).upper()

    return wrapper
```
---
# From class decorators to meta classes

with decorators
## we can modify how classes are called or do stuff before initialization
## we can create singeltons or factories
???
https://www.youtube.com/watch?v=sPiWg5jSoZI&feature=youtu.be
But ... this only apply to deocrated classes and not subclasses.
---
# Metaclasses

 - in short YAGNI
 - really?

---
## Metaclasses

### An example with SessionManager

I want to write a base class of session managers for users
that want to create other managers.

For example session store in a file, Redis or another database.

???

---
### JAVA Interface style

```python
class BaseSessionManager(object):

    def __init__(self, *args, **kwargs):
        """
        Use this to create database connections, etc.
        """
        pass

    def __setitem__(self, id, data):
        raise RuntimeError("Session manager must override __setitem__")

    def __getitem__(self, id):
        raise RuntimeError("Session manager must override __getitem__")

    def __contains__(self, id):
        raise RuntimeError("Session manager must override __contains__")

# silently possible
class RedisSessionManager(BaseSessionManager):
     pass
```
???

Disatvantage: Will explode only at run time (a JAVA complier will
catch this at compile time).

See:
   https://github.com/oz123/WSGISession/blob/master/wsgisession.py#L9
---
###  Metaclasses

```
class BaseSessionMeta(type):

    def __new__(meta, name, bases, class_dict):
        # Don’t validate the abstract BaseSession class
        if bases != (object,):
            for item in ['__setitem__', '__getitem__', '__contains__']:
                method = class_dict.get(item)
                if not method or not inspect.isfunction(method):
                    raise ValueError(
                        '{} must define a method called {}'.format(name, item))
        return type.__new__(meta, name, bases, class_dict)

class BaseSession(object, metaclass=BaseSessionMeta):
    pass

# you can't do this:
class RedisSession(BaseSession):
    pass

```
???

This will crash before run time!

see
   https://github.com/oz123/WSGISession/blob/base_meta/wsgisession.py#L24
