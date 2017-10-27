Sessions
========

Sessions are a mechanism to persists the user's interaction with the website.
Usually, sessions really on reading a unique session ID from the information
stored in the browser.
This information stored in the browser is usually stored in a cookie.

To implement a session storage which behave like a dictionary, we take
advantage of the Python data model. Before we actually, implement the Session
class, we take a look on how Python accesses attributes of objects and their
instances.


Attrbitute access
-----------------

Attributes are everything found in a an object instance. Attributes are, usually,
stored in an instance`s ``__dict__``, but we will see shortly, how this is only
partially true. Let's look at an instance ``p`` of the class ``Person``:

.. code:: python

   >>> class Person:
   ...     def __init__(self, name, last_name):
   ...         self.name = name
   ...         self.last_name = last_name
   ...
   >>> p = Person("Alan", "Turing")
   >>> p.__dict__
   {'last_name': 'Turing', 'name': 'Alan'}

When accessing ``p.name`` there is a chain of lookups of ``p`` in a few places.
A look up in ``p.__dict__`` is almost the last action. The following examples,
reveal gradually the full attribute access chain.

>>> class Person:
...     def __init__(self, name, last_name):
...         self._name = name
...         self.last_name = last_name
...     def __name(self):
...         return self._name.capitalize()
...     def __name_set(self, value):
...         self.__name = value
...     name = property(__name, __name_set)
...
>>> p = Person("alan", "Turing")
>>> p.name
'Alan'
>>> p.__name
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'Person' object has no attribute '__name'
>>> p._name
'alan'
>>> p.__dict__
{'_name': 'alan', 'last_name': 'Turing'}
>>> p.
p._Person__name(      p.__dir__(            p.__getattribute__(   p.__lt__(             p.__reduce_ex__(      p.__subclasshook__(   
p._Person__name_set(  p.__doc__             p.__gt__(             p.__module__          p.__repr__(           p.__weakref__         
p.__class__(          p.__eq__(             p.__hash__(           p.__ne__(             p.__setattr__(        p._name               
p.__delattr__(        p.__format__(         p.__init__(           p.__new__(            p.__sizeof__(         p.last_name           
p.__dict__            p.__ge__(             p.__le__(             p.__reduce__(         p.__str__(            p.name                
>>> p.__weakref__
>>> Person
<class '__main__.Person'>
>>> Person.__dict__
mappingproxy({'__module__': '__main__', 'name': <property object at 0x7f1d409772c8>, '_Person__name': <function Person.__name at 0x7f1d4097c598>, '__weakref__': <attribute '__weakref__' of 'Person' objects>, '_Person__name_set': <function Person.__name_set at 0x7f1d4097c620>, '__init__': <function Person.__init__ at 0x7f1d40974158>, '__dict__': <attribute '__dict__' of 'Person' objects>, '__doc__': None})


Attribute access the full picture
---------------------------------




The full session middleware
---------------------------

.. code:: python

   import uuid
   from http.cookies import SimpleCookie


   class DictBasedSessionStore:
       """
       A reference store, which stores items in a global dictionary.

       This in not suitable for a real usage (e.g. an application which
       run with multiple workers)
       """

       sessions = {}

       def __setitem__(self, id, data):
           self.sessions[id] = data

       def __getitem__(self, id):
           return self.sessions[id]

       def __contains__(self, id):
           return id in self.sessions


   class SimpleSession:

       def __init__(self, storage, id=None):
           self.store = storage
           self.data = {}
           self.load(id)

       def __getitem__(self, key):
           return self.data[key]

       def __setitem__(self, key, value):
           self.data[key] = value

       def get(self, key, default=None):
           if key in self.data:
               return self.data[key]

           return default

       def load(self, id):
           """
           Find id in storage, if failed create a new ID.

           """
           if id in self.store:
               self.data = self.store[id]
               self.id = id
           else:
               self.data = {}
               self.id = uuid.uuid4().hex

       def save(self):
           self.store[self.id] = self.data
           return self.id


   class SimpleSessionMiddleware:
       """
       This middleware injects a SimpleSession instance to the envrionment
       passed to the application.

       You can than put anything you want in this instance of session.

       """
       def __init__(self, app, session_manager=DictBasedSessionStore,
                    env_key='wsgisession', cookie_key='session_id'):
           self.app = app
           self.env_key = env_key
           self.cookie_key = cookie_key
           self.manager = session_manager()

       def __call__(self, environ, start_response):
           cookie = SimpleCookie()
           if 'HTTP_COOKIE' in environ:
               cookie.load(environ['HTTP_COOKIE'])

           id = None
           if self.cookie_key in cookie:
               id = cookie[self.cookie_key].value

           session = SimpleSession(self.manager, id=id)
           environ[self.env_key] = session

           def middleware_start_response(status, response_headers, exc_info=None):

               session.save()
               cookie = SimpleCookie()
               cookie[self.cookie_key] = session.id
               cookie[self.cookie_key]['path'] = '/'
               cookie_string = cookie[self.cookie_key].OutputString()
               response_headers.append(('Set-Cookie', cookie_string))
               return start_response(status, response_headers, exc_info)

           return self.app(environ, middleware_start_response)
