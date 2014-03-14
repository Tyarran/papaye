.. image:: https://travis-ci.org/rcommande/papaye.png?branch=master   :target: https://travis-ci.org/rcommande/papaye

papaye README
==================
A basic PyPi server clone written in `Pyramid Web Framework`_, using `CodernityDB`_ and `Beaker Cache`_.

**This is EXPERIMENTAL. Do not install Papaye in production!**

Getting Started
---------------

- cd <directory containing this file>

- $venv/bin/python setup.py develop

- $venv/bin/papaye_init development.ini

- $venv/bin/pserve development.ini


.. _CodernityDB: http://labs.codernity.com/codernitydb/
.. _Pyramid Web Framework: http://www.pylonsproject.org
.. _Beaker Cache: http://beaker.readthedocs.org