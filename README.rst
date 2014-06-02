.. image:: https://travis-ci.org/rcommande/papaye.png?branch=master   :target: https://travis-ci.org/rcommande/papaye

papaye README
==================
A basic PyPi server clone written in `Pyramid Web Framework`_, using `ZODB`_ and `Beaker Cache`_.

**This is EXPERIMENTAL. Do not install Papaye in production!**

Getting Started
---------------

- cd <directory containing this file>
- $venv/bin/pip install -e .
- $venv/bin/papaye_init development.ini
- $venv/bin/runzeo -C zeo.conf
- $venv/bin/pserve development.ini  # Use production.ini in production


.. _ZODB: https://pypi.python.org/pypi/ZODB
.. _Pyramid Web Framework: http://www.pylonsproject.org
.. _Beaker Cache: http://beaker.readthedocs.org
