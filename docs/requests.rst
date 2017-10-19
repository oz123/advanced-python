The Request class - an environment wrapper
==========================================

Until now we have seen that a simple WSGI application
receives the ``environment`` and ``start_request`` handler.
While not to complicated to use, most modern Python web framework
provide s ``Request`` class that wraps the environment.
This class has dynamincally caluculated properties and is allowing
a more convinient way to access values of keys in the environment
dictionary as if the where instance attributes.

We have already seen how we can create classes that behave like
dictionaries. But now are seeking to implement the opposite.


Excercise 7
+++++++++++

Implement a class which accepts a dictionary in its constructor,
allows accessing its keys as if they where attributes

.. code:: python

   >>> env_wrapper = Request(envrionment)
   >>> env_warpper.PATH_INFO ==  environ.get('PATH_INFO'))
   True

..  admonition:: Solution
    :class: toggle

    .. code-block:: python

        env = {"PATH_INFO": "/login/"}


        class Request:

            def __init__(self, environ):
                self.from_env(environ)

            def from_env(self, env):
                for k, v in env.items():
                    setattr(self, k, v)
