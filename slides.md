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
## From the Browser to Python and back
![](./static/http-server-app.svg)
---
## WSGI Servers

![](./static/wsgi-servers.svg)

---
layout: false
class: left
## Hello World in WSGI

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
## Invoking your WSGI application

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
## Can you write a WSGI app with a class?

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
## Middlewares in Work

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
## Plumbing Middlewares

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
## Plumbing middlewares example

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
## From raw WSGI to a web framework

 * pre-process the `environment`
   - yield a `request` object to work with
 * route `PATH_INFO` to your views
 * add session management
 * ship some common middlewares and classes to create valid HTTP responses
 * add some HTML templating
 * Optionally give you some data storage layer

---
## Cookies and Sessions

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
## Attribute access
### Class access
```
Item.x -> Item.__dict__['x']
```
### Instance attribute access (approximately)

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
## Attribute Access demo:
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
### assign, retrieve and delete chunks of list like objects
```
def __getitem__(self, key):
    if isinstance(key, slice):
        return [self.list[i] for i in range(key.start, key.stop, key.step)]
    return self.list[key]
```
### Checking membership
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
## Closures

```python
>>> def startAt(start):
...     def incrementBy(inc):
...             return start + inc
...     return incrementBy
...
>>> f = startAt(10)
>>> g = startAt(100)
>>>
>>> print f(1), g(2)
11 102
```
???

Using a nested function we can make a "template" for function, or function factories.
A nested function has access to the environment in which it was defined.
This is called a closure.

---
## Closures with Lexical scoping
```python
>>> def count_from(a):
...     count = [a]
...     def incrementer(step):
...         count[0] += step
...         return count[0]
...     return incrementer
...
>>> start_at_hundred = count_from(100)
>>> start_at_hundred(2)
102
>>> start_at_hundred(3)
105
>>> start_at_five = count_from(5)
>>> start_at_five(3)
8
```
???
The definition of a closure occurs during the execution of the outer function.
Hence, it is possible to return an inner function that remembers the state of
the outer function, even after the outer function has completed execution.

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
## Syntactic sugar

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
## higer order functions

???

Decorators are also high order functions. The pattern of wrapping a function with
another function is so common that Python has a special syntax for it.
A powerful and common, albeit slightly complex, paradigm in Python is the use
of function decorators. The usual role of decorators is to reduce repetition in
code by consolidating common elements of setup and teardown in functions.

The second building block is a closure. Remember that a nested, or inner,
function in Python has access to the environment in which it was defined.
If that environment happens to include another function, then the closure will
have access to that function.

---
## Class based decorators

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
## Class decorators

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
???

---
## Class based class decorators

 - Implement a class decorator which makes all attributes read only
 - Hint: the modified class overrides both `__getattr__` and `__setattr__`

???

---
## Decorators with (optional) arguments
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
# a good example
http://stackoverflow.com/a/653478/492620

Keyword only syntax.
https://www.python.org/dev/peps/pep-3102/

---
## Decorators with arguments
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
## Decorators with arguments
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
## From class decorators to meta classes

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

    def __new__(meta, name, bas:es, class_dict):
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

---
class: center, middle, inverse
# Part 3 - Functional Python

---
#  What is functional programming?

 * A programming paradigm
 * In a way, opposite of object-oriented programming
 * Has lot's of nerdy terms like: immutable data, first class functions,
   currying, high order function.
    - they all make you feel either really smart or really stupid.
 * `No Side Effects`

???

Essentially after all these bullet points, functional code is
characterised by one thing: the absence of side effects.
It doesn’t rely on data outside the current function,
and it doesn’t change data that exists outside the current function.
Every other “functional” thing can be derived from this property.

citation from:
https://codewords.recurse.com/issues/one/an-introduction-to-functional-programming

---
# Why should you care? Why do I care?

## OOP vs. FP
.img-left[![-clip-b](./static/OOP.jpg)]

???

Object Oriented Code can be very complex to master, and as such very hard to
maintain. Functional Programming forces us to avoid side effects and as a result
allows us to gain control over program development, and eases maintenance.

This are not just academicly speeking. I have had to maintain very complex OO
based codes in the past. Promoting FP style, is my way to make my job as a
developer a bit easier.

---

# Why should you care? Why do I care?

## OOP vs. FP
.img-left[
![-clip-b](./static/OOP.jpg)
]
.img-right[

![-resize-50](./static/fp2.jpg)
]

???

Object Oriented Code can be very complex to master, and as such very hard to
maintain. Functional Programming forces us to avoid side effects and as a result
allows us to gain control over program development, and eases maintenance.

This are not just academicly speeking. I have had to maintain very complex OO
based codes in the past. Promoting FP style, is my way to make my job as a
developer a bit easier.

---

![-resize-b](./static/banana.jpg)

???

Let me cite Joe Armstrong, the creator of the functional programming language,
Erlang:
"The problem with object-oriented languages is they’ve got all this implicit
environment that they carry around with them. You wanted a banana but what
you got was a gorilla holding the banana and the entire jungle."

The citation is taken from the book Coders at Work.

OK. So now that we set the right mood and are the with the indroduction, let's
see how functional Python is.

---
# How functional is Python?

 * First Class Functions
 * Built-ins such as `map, filter, lambda, all, any, zip, enumerate, sorted`
 * Special Syntax for List and Dictionary comprehensions.
 * functional tools in the standard library modules: `itertools, functools, operator`
 * Higher order functions, closures, decorators.
 * Generators and lazy evaluation with `yield`.

???

Wikipedia tells us that:
"Python supports multiple programming paradigms,
including object-oriented, imperative and functional programming or procedural
styles."

But let's break it down:

Python has First Class Functions, which means that functions are objects.
Functions have attributes, they can be referenced and assigned to variables.

Python has many builtin functions and standard library tool which encourage
functional programming style.

It also has a special syntax for manipulating iterable object known as list and
dictionary comperhensions.

It can do lazy evaluation and has so called `generators`.

Decorators are commonly used to wrap functions with other functions. This is
other which knows as `High Order Function`. This simply a function that takes
another function as it's argument.

So, we've got a lot of ground to cover. Let's start!

---
## Functional style functions

A function which changes stuff out of scope ...

```python
a = 0
def no_functional_increment():
    """vicicous side effects"""
    global a
    a += 1
```
---
## Functional style functions
Adhere to change stuff localy:

```python
def functioal_increment(a):
    """increment a inside and return the incremented value"""
    return a + 1
```

---
## No to `for` loops:

```python
newlist = []
for word in oldlist:
    newlist.append(word.upper())
```

## Say yes to `map`:
```python
newlist = map(str.upper, oldlist)
```
## or use a list comperhension
```python
newlist = [s.upper() for s in oldlist]

```

???

Every time you want to write a for loop, stop!
Use map or a list comperhension. As a side bonus, map in Python is faster, and
a list comprehension is even faster.
You can think of map as a for moved into C code. The only restriction is that
the "loop body" of map must be a function call. Besides the syntactic benefit
of list comprehensions, they are often as fast or faster than equivalent use
of map.
See https://wiki.python.org/moin/PythonSpeed/PerformanceTips

---
## you can also apply any function
```python
>>> map(lambda x: x**2, range(1,4))
[1, 4, 9]
```
List comperhension use a slightly different syntax
```python
>>> [x**2 for x in  range(1,4)]
[1, 4, 9]
```
This of course too

```python
[some_function(x) for x in  range(1,4)]
```
???

Map does not only work with object's methods. It takes any function, including
lambda functions.
List comperhension except also expersions, not only functions. We'll see more
of list comperhensions later.

Maps and List comperhensions can be used on other objects than lists. These
are all itrable objects.

---
# iterable

```
An object capable of returning its members one at a time.
Examples of iterables include all sequence types
(such as list, str, and tuple)
and some non-sequence types like dict and file and
objects of any classes you define with an `__iter__()`
or `__getitem__()` method.
Iterables can be used in a for loop and in many
other places where a sequence is needed
(`zip()`, `map()`, ...).
```
???

<small>This definition is taken from the Python glossary</small>

---
# Using `filter`

```python
>>> def is_even(x):
...     return (x % 2) == 0
>>> list(filter(is_even, range(10)))
[0, 2, 4, 6, 8]
```
We can write this a list comperhension too:
```python
>>> list(x for x in range(10) if is_even(x))
[0, 2, 4, 6, 8]
```
???

---
# all and any
```python
>>> any([0,1,0])
True
>>> any([0,0,0])
False
>>> any([1,1,1])
True
>>> all([0,1,0])
False
>>> all([0,0,0])
False
>>> all([1,1,1])
True
```
???
The any(iter) and all(iter) built-ins look at the truth values of an iterable’s
contents. any() returns True if any element in the iterable is a true value,
and all() returns True if all of the elements are true values:--

---
## sorted
```python
>>> import random
>>> # Generate 8 random numbers between [0, 10000)
>>> rand_list = random.sample(range(10000), 8)
>>> rand_list
[769, 7953, 9828, 6431, 8442, 9878, 6213, 2207]
>>> sorted(rand_list)
[769, 2207, 6213, 6431, 7953, 8442, 9828, 9878]
>>> sorted(rand_list, reverse=True)
[9878, 9828, 8442, 7953, 6431, 6213, 2207, 769]
```

---
## sorted

### entries is a list containing  blog posts, each with a date attribute.

```python
def _sort_entries(entries, reversed=True):
    """Sort all entries by date and reverse the list"""
    return list(sorted(entries,
                       key=operator.attrgetter('date'),
                       reverse=reversed))
```

???

collects all the elements of the iterable into a list, sorts the list, and
returns the sorted result. The key and reverse arguments are passed through
to the constructed list’s sort() method.

---
# zip

```python
>>> zip(['a', 'b', 'c'], (1, 2, 3))
[('a', 1), ('b', 2), ('c', 3)]

>>> zip(['a', 'b'], (1, 2, 3))
[('a', 1), ('b', 2)]
```
???
zip(iterA, iterB, ...) takes one element from each iterable and returns them in a tuple.
It doesn’t construct an in-memory list and exhaust all the input iterators before returning;
instead tuples are constructed and returned only if they’re requested.
(The technical term for this behaviour is lazy evaluation.)

This iterator is intended to be used with iterables that are all of the same length.
If the iterables are of different lengths, the resulting stream will be the
same length as the shortest iterable.

---
# List Comprehensions

Instead of an embeded for loop:

```python
>>> colors = ['red', 'yellow', 'blue']
>>> clothes = ['hat', 'shirt', 'pants']
>>> colored_clothes = ['{0} {1}'.format(
... color, garment) for color in colors
                        for garment in clothes]
>>> colored_clothes
['red hat', 'red shirt', 'red pants', ...
 'blue hat', 'blue shirt', 'blue pants']
```
---
# List Comprehensions

The alternative would be:
```python
colored_clothes = []

for color in color:
    for garment in clothes:
        colored_clothed.append(
... '{0} {1}'.format(color, garment))
```

???

as mentioned before, the prefered way to iterate over iterators, instead of for
loop.

---
## dictionary and set comprehensions:
```python
>>> {k:v for (k,v) in zip(['a', 'b', 'c'], (1, 2, 3))}
{'a': 1, 'c': 3, 'b': 2}

>>> def invert(d):
...     return {v : k for k, v in d.iteritems()}
...
>>> d = {0 : 'A', 1 : 'B', 2 : 'C', 3 : 'D'}
>>> print invert(d)
{'A' : 0, 'B' : 1, 'C' : 2, 'D' : 3}
```

set comprehensions:

```python
>>> list(range(10)) + [1,2,3]
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 2, 3]
>>> { x for x in list(range(10)) + [1,2,3] }
{0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
```
???

The little unknown relative of list comprehensions, originally proposed for Python 2.3.
It was however only included in Python 2.7 and Python 3.0 and later versions.

Set comprehensions have a very similar syntax!

---
## The `functools` and `operator` modules
```python
# implement factorial
>>> import functools
>>> functools.reduce(lambda x,y: x*y, [1,2,3,4])
24
```
This can also be written as:
```python
>>>import operator
>>> functools.reduce(operator.mul, [1,2,3,4])
24
```

???
So,we finaly finished the built-is part. And now we get say some sexy stuff like
high order functions.

A higher-order function takes one or more functions as input and returns a new
function. The most useful tool in this module is the functools.partial()
function.

The functools module in Python 2.5 contains the reduce function and some other
higher-order functions.

The operator module:
It contains a set of functions corresponding to Python’s operators.
These functions are often useful in functional-style code because they save
you from writing trivial functions that perform a single operation.

Some of the functions in this module are:

    Math operations: add(), sub(), mul(), floordiv(), abs(), ...
    Logical operations: not_(), truth().
    Bitwise operations: and_(), or_(), invert().
    Comparisons: eq(), ne(), lt(), le(), gt(), and ge().
    Object identity: is_(), is_not().

---
# Partial Functions

```python
 functools.partial(func, *args, **keywords)
```
A simple example:

```python
>>> import functools
>>> def log(message, subsystem):
...     """Write the contents of 'message'
        to the specified subsystem."""
...     print('%s: %s' % (subsystem, message))
...
>>> server_log = functools.partial(log, subsystem='server')
>>> server_log('Unable to open socket')
server: Unable to open socket
```
???
Factory functions are also very common, and for more complex closure function,
we the partial constructor.
The constructor for partial() takes the arguments
(function, arg1, arg2, ..., kwarg1=value1, kwarg2=value2).
The resulting object is callable, so you can just call it to invoke function with the filled-in arguments.

---
## functools.partial examples:
```python
>>> def generic_filter(obj, klass, func, exception):
...     """this function makes no real sense, yet ..."
...     if isinstance(obj, klass):
...         return func(obj)
...     else:
...         raise exception
...
>>> safe_add_3 = partial(generic_filter, klass=int,
                         func=lambda x: x+3,
                         exception=ValueError(
                         "You didn't give an int"))
>>> safe_add_3(5)
8
>>> safe_add_3("three")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 6, in generic_filter
ValueError: You didn't give an int
```
---

## functools.partial examples:

```python
>>> safe_replace_str = partial(generic_filter, klass=str,
    func=lambda obj: obj.replace("Foo", "bar"),
    exception=ValueError("You didn't give a str"))
>>> safe_replace_str("Foobaz"),
'barbaz'
>>> safe_replace_str({})
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "<stdin>", line 6, in generic_filter
ValueError: You didn't give a str
```

---
## Generators
### lazy evalutaion of list comprehensions
```python
>>> (x**2 for x in  range(1,4))
<generator object <genexpr> at 0x7f7672c992b0>
>>> next((x**2 for x in  range(1,4)))
1
>>> for item in (x**2 for x in  range(1,4)): print(item,)
...
1
4
9
```
???
Storing a new list as the output of a list comprehension is not always optimal
behavior. Particularly in a case where that list is intermediary or
where the total size of the contents is quite large.

For such cases, a slightly modified syntax
(replacing square brackets with parentheses) leads to the creation of a
generator instead of a new list.
The generator will produce the individual items in the list as each one is
requested, which is generally while iterating over that new list.

---
## Generator functions
```python``
>>> def generate_ints(N):
...    for i in range(N):
...        yield i

>>> gen = generate_ints(3)
>>> gen
<generator object generate_ints at 0x7f7672c99308>
>>> next(gen)
0
>>> next(gen)
1
...
>>> next(gen)
Traceback (most recent call last):
  File "stdin", line 1, in ?
  File "stdin", line 2, in generate_ints
StopIteration
```
???

Generators are a special class of functions that simplify the task of
writing iterators. Regular functions compute a value and return it,
but generators return an iterator that returns a stream of values.

Any function containing a yield keyword is a generator function;

When you call a generator function, it doesn’t return a single value;
instead it returns a generator object that supports the iterator protocol.
On executing the yield expression, the generator outputs the value of i,
similar to a return statement.
The big difference between yield and a return statement is that on reaching a
yield the generator’s state of execution is suspended and local variables
are preserved.
On the next call to the generator’s __next__() method,
the function will resume executing.

---
### execution halt after `yield`:
```python
>>> def generate_ints(N):
...     count = 1
...     for i in range(N):
...         count += 1
...         yield i
...         print("I gave you {}. {} more to go ...".format(i, N-count))
...
>>> g = generate_ints(5)
>>> next(g)
0
>>> next(g)
I gave you 0. 3 more to go ...
1
...
>>> next(g)
I gave you 4. -1 more to go ...
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
StopIteration
```

---

# putting all together
## let's create a functional solution

???

So, who here does not know the fizzbuzz game?
explain the game shortly.

---

```python
# Naive implementation ... with a for loop

for i in range(1,21):
    if not i % (5*3):
        print("fizzbuzz")
    elif not i % 5:
        print("fizz")
    elif not i % 3:
        print("buzz")
    else:
        print(i)
# 9 lines
```
---
## home-brewed `range`
```python
>>> def range_(stop):
...     '''home brewed range replacement'''
...     n = 0
...     while stop > n:
...         yield n
...         n += 1
...
>>> [i for i in range_(5)]
[0, 1, 2, 3, 4]
```
---
## closures to create `fizz` `buzz` filters
```python
>>> def fizzbuzzfilter(test,num, word):
...     if (type(test) != int) or (test%num):
...         return test
...     else:
...         return word
...
>>> def fizzbuzzfilter3(test):
...     return fizzbuzzfilter(test, 3, "fizz")
...
>>> def fizzbuzzfilter5(test):
...     return fizzbuzzfilter(test, 5, "buzz")
...
>>> def fizzbuzzfilter15(test):
...     return fizzbuzzfilter(test, 15, "fizzbuzz")
...
>>> fizzbuzzfilter3(3), fizzbuzzfilter3(5), fizzbuzzfilter3(None)
('fizz', 5, None)
```

???

## closures to create `fizz` `buzz` filters
>>> list(map(fizzbuzzfilter5, map(fizzbuzzfilter3, map(fizzbuzzfilter15, range(1,21)))))
[1, 2, 'fizz', 4, 'buzz', 'fizz', 7, 8, 'fizz', 'buzz', 11, 'fizz', 13, 14, 'fizzbuzz', 16, 17, 'fizz', 19, 'buzz']

Multiple maps

This approach works, but it does violates the DRY principle.
It's not very readable.
The STL offers a nice wrapper called partial,
for creating exactly that.

---
## using partial for fizzbuzz filters
```python
from functools import partial
filter3 = partial(fizzbuzzfilter, num=3, word='fizz')
filter5 = partial(fizzbuzzfilter, num=5, word='buzz')
filter15 = partial(fizzbuzzfilter, num=15, word='fizzbuzz')
print(list(map(filter5, map(filter3, map(filter15, range(1,21))))))
```
### OK, it works, and it's more conviniet to write,
### but it's still not very readable.

---
### map multiple functions
### no DRY and slightly more readable

```python
def map_many(iterable, function, *other):
    """map many functions to a single iterable"""
    if other:
        return map_many(map(function, iterable), *other)
    return map(function, iterable)

list(map_many(range(1,21), filter15, filter3, filter5))
```
### but this approach is a bit expensive.
```python
%timeit list(map_many(range(1,21), filter15, filter3, filter5))
10000 loops, best of 3: 26.3 µs per loop
```
---
### A slightly better approach with `yield`
```python
from functools import partial

filter3 = partial(fizzbuzzfilter, num=3, word='fizz')
filter5 = partial(fizzbuzzfilter, num=5, word='buzz')
filter15 = partial(fizzbuzzfilter, num=15, word='fizzbuzz')

def fizzbuzzfiltery(numbers, num, word):
    for test in numbers:
        if (type(test) == str) or (test%num):
            yield test
        else:
            yield word

filter3y = partial(fizzbuzzfiltery, num=3, word='fizz')
filter5y = partial(fizzbuzzfiltery, num=5, word='buzz')
filter15y = partial(fizzbuzzfiltery, num=15, word='fizzbuzz')
nums = range(1,21)
list(filter5y(filter3y(filter15y(nums))))
#%timeit list(filter5y(filter3y(filter15y(nums))))
#100000 loops, best of 3: 12.2 µs per loop
```
---
### Not only ponies in functional programming

 * Sometimes FP is harder to read and write

```python
  # replace query for Boolean fields
  # get all field names
  fields = {k: v.groups()[0] for k, v in
            dict(filter(lambda x: x[1] is not None,
                 map(lambda x: (x, re.search('(^\w+)__', x)),
                     d.keys()))).items()}
```
![](./static/lisp_cycles.png)
---
## Not only ponies in functional programming

 * Functions calls are expensive in Python
 * Python does not have good recursion (essential in classical FP languages)

---
## key points about functional programming

 * FP can make your code easier to follow
 * Avoid side effects
 * Not everything has to be in a class (although in Python everything is
 an object)
 * Use high order functions, think of data flow, not of states.


???

[An introduction to functional programming][1]
[Python Doc - FP how to][2]
[Advanced iterations - The new Circle][3]
[1]: https://codewords.recurse.com/issues/one/an-introduction-to-functional-programming
[2]: https://docs.python.org/dev/howto/functional.html
[3]: https://newcircle.com/bookshelf/python_fundamentals_tutorial/advanced_iterations

---
### Image credits

 - Clean server cables - https://www.flickr.com/photos/kenfagerdotcom/
 - Banana - https://www.flickr.com/photos/robin24/
 - xkcd.com for the comic strip

