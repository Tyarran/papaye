.. image:: https://travis-ci.org/rcommande/papaye.png?branch=master
    :target: https://travis-ci.org/rcommande/papaye

Papaye
======
Yet another Python Package Repository (local PyPI) written with the `Pyramid Web Framework`_, using `ZODB`_ and `Beaker Cache`_.

Getting Started
---------------

::

    cd <directory containing this file>
    $venv/bin/pip install -e .
    $venv/bin/papaye_init development.ini  # Use production.ini in production
    $venv/bin/pserve development.ini  # Use production.ini in production


Migrate the application from an older version
---------------------------------------------

::

    papaye_evolve you_configuration_file.ini

Configuration
-------------

Papaye variables
################

.. list-table:: Papaye variables
   :header-rows: 1
   :stub-columns: 1

   * - Parameter
     - Type
     - Description
   * - papaye.proxy
     - true / false
     - Enable proxy from PyPI server functionality
   * - papaye.anonymous_install
     - true / false
     - Allow anonymous user to install packages
   * - papaye.cache
     - true / false
     - Enable Papaye cache functionality
   * - papaye.scheduler
     - Python module
     - Set the Papaye scheduler
   * - papaye.scheduler.workers
     - Integer
     - Set worker concurency value


.. _ZODB: https://pypi.python.org/pypi/ZODB
.. _Pyramid Web Framework: http://www.pylonsproject.org
.. _Beaker Cache: http://beaker.readthedocs.org
