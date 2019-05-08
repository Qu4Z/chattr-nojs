chattr
======

A fork of https://github.com/philipkorsika/chattr

This version removes the need for JavaScript! 

(note that it still uses CSS for aesthetics, but it's not necessary for the functionality, and would work without it)

Install
-------

Requires Python and Python dev-tools, and [pip installed](http://python-packaging-user-guide.readthedocs.org/en/latest/installing/#install-pip-setuptools-and-wheel) 

e.g. On Ubuntu 15.10 :

```bash
$ python -V
=> Python 2.7.10
$ sudo apt-get install python2.7-dev python-pip
```

Install bottle and gevent, then start the server.
```bash
$ pip install --user bottle gevent
$ python server.py
```

Browse to `localhost:9092`

