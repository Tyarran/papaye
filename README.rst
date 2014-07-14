.. image:: https://travis-ci.org/rcommande/papaye.png?branch=master
    :target: https://travis-ci.org/rcommande/papaye

papaye
======
A basic PyPi server clone written in `Pyramid Web Framework`_, using `ZODB`_ and `Beaker Cache`_.

Getting Started
---------------

- cd <directory containing this file>
- $venv/bin/pip install -e .
- $venv/bin/papaye_init development.ini  # Use production.ini in production
- $venv/bin/pserve development.ini  # Use production.ini in production


Configuration
-------------

Papaye variables
################

papaye.proxy (true / false)
...........................
Enable proxy from Pypi server

papaye.anonymous_install (true / false)
.......................................
Allow anonymous user to install packages

papaye.proxy.broker (ZMQ URI)
.............................
ZMQ URI used by queue and producer devices

papaye.proxy.collector (zmq uri)
................................
zmq uri used by collector device

papaye.proxy.worker (zmq uri)
.............................
zmq uri used by worker devices

papaye.worker.concurency (integer)
..................................
Number of workers


.. _ZODB: https://pypi.python.org/pypi/ZODB
.. _Pyramid Web Framework: http://www.pylonsproject.org
.. _Beaker Cache: http://beaker.readthedocs.org
