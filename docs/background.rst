The Web and Python
==================
In the days before the popularity of frameworks like Django, Flask
and other frameworks soared, development with Python for the web was
a bit harder for comers.

Python applications were often designed for only one of CGI,
FastCGI, mod_python or some other custom API of a specific web server.
This wide variety of choices can be a problem for new Python users,becausegenerally speaking, their choice of web framework limited
their choice of usable web servers, and vice versa.


WSGI
---
 
WSGI was created as a low-level interface between web servers and
web applications or  frameworks to promote a common ground for
portable web application development. This is similar to Java's
"servlet" API makes it possible for applications written with any
Java web application framework to run in any web server that
supports the servlet API. [pep-333]                    

As stated above, WSGI was created to ease the development of Python
web applications. The handling of the requests from browser is done
by a normal HTTP server, which routes the request to the WSGI container,
which in turn runs the WSGI application.

The following ilustration demonstartes this setup:



This setup promotes scalability and flexibility. Handling of HTTP request
is done best by HTTP servers, put a load balancer in front, and you can
easily scale to thousands of requests with out having to modify your
Python code. Know a better server? a better framework? You can replace
on WSGI server without having to change your code. You have an alreay
working application but you want to add features using a different
WSGI framework? No problem with that either, you can built application
with different frameworks, as long as they all support WSGI.


