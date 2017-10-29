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
A look up in ``p.__dict__`` is almost the last action. We will discuss the
complete process of attribute access later. For now, we are going to stay with
this partially correct image.

If the attribute we are trying to access is not found in the instances
`__dict__` the same attribute will be searched in the class ``__dict__``.

.. code:: python

        >>> class Person:
        ...     scientific_name = 'Homo Sapiens'
        ...     def __init__(self, name, last_name):
        ...         self.name = name
        ...         self.last_name = last_name
        ...
        >>> p = Person('Alan', 'Turing')
        >>> p.__dict__
        {'last_name': 'Turing', 'name': 'Alan'}
        >>> p.scientific_name
        'Homo Sapiens'
        >>> Person.__dict__
        mappingproxy({'__module__': '__main__', '__weakref__': <attribute '__weakref__' of 'Person' objects>, 'scientific_name': 'Homo Sapiens', '__init__': <function Person.__init__ at 0x7f1d4097c6a8>, '__dict__': <attribute '__dict__' of 'Person' objects>, '__doc__': None})
        ```

We have shown that attributes are instance attributes or class attributes, which
are saved in an underlying ``__dict__`` associated with the instance or the class.
We could use that underying ``__dict__`` or even make a class with an attribute
of type ``dict`` that holds the session data. We will the have to either use
some method to put data in that dictinary or always access this dictionary, for
example::


     >>> session = SessionStorge()
     >>> session.store_session({{"id": {"k": "v" ...})
     # the above method saved the date inside the underlying session.__dict__

or, by access the storage attribute::

     >>> session.store["id"] = {"k", "v" ...}

The first method is very unpythonic, and addes and extra method call. The second
method just added a new underlying attribute, so everytime we access the store,
the interpreter needs to do an extra step to first pick up ``store`` from
``session.__dict__`` and then store an item in an embeded ``__dict__`` within.

As already pointed above, we want our SessionStorage class to behave like a
dictionary. To do that we need to create a class with a few special methods.
Specifically, we are going to create a ``__getitem__`` method which alows
us to access the session data with ``session['session_id']``.

Exercise 6
+++++++++++

Implement a ``PhoneBook`` class with a ``__getitem__`` method.
The class should have the following ``__init__``:


   >>> class PhoneBook:
   ...      def __init__(self, phones):
   ...          self.phones = dict(phones)



   >>> class PhoneBook:
   ...      def __init__(self, phones):
   ...          self.phones = dict(phones)
   ...      def __getitem__(self, item):
   ...          try:
   ...              return self.phones[item]
   ...          except KeyError:
   ...              raise KeyError("%s not found in phonebook" % item)
   ...

   >>> p = PhoneBook([("Alan", '+447737238400'), ("Edgar", "+17737328230")])
   >>> p.phones
   {'Edgar': '+17737328230', 'Alan': '+447737238400'}
   >>> p['Alan']
   '+447737238400'
   >>> p['Homer']
   Traceback (most recent call last):
     File "<stdin>", line 6, in __getitem__
   KeyError: 'Homer'

   During handling of the above exception, another exception occurred:

   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "<stdin>", line 8, in __getitem__
   KeyError: 'Homer not found in phonebook'

This class isn't very usefull if we can't also update the underlying phone book.
Let's add a  ``__setitem__`` to it.

>>> class PhoneBook:
...      def __init__(self, phones):
...          self.phones = dict(phones)
...      def __getitem__(self, item):
...          try:
...              return self.phones[item]
...          except KeyError:
...              raise KeyError("%s not found in phonebook" % item)
...      def __setitem__(self, key, value):
...          self.phones[key] = value
...
>>> p = PhoneBook([("Alan", '+447737238400'), ("Edgar", "+17737328230")])
>>> p['Homer'] = '+303128234499'


Addmitidly, the need to add an intermediate attribute ``phones`` seems
rudimentary. So let's get rid of it.


class PhoneBook:
     def __init__(self, phones):
         for (key, value) in phones:
            setattr(self, key, value)
     def __getitem__(self, item):
         try:
             return getattr(self, item)
         except AttributeError:
             raise KeyError("%s not found in phonebook" % item)
     def __setitem__(self, key, value):
         setattr(self, key, value)


So now that got rid of the attribute ``phones``, it is important to empasize
that we can do what ever we like in ``__setitem__`` and ``__getitem__``, that
is in addition to modifying the object itself. We can pickle data to file, and
unpickle it from a file, store and retrieve it from an SQL datbase or Redis
storage.


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
