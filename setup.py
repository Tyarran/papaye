# -*- coding:utf-8 -*-
import os

from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.txt')).read()
VERSION = '0.1.3-dev'

requires = [
    'colander',
    'cornice',
    'docutils',
    'filemagic',
    'pyramid',
    'pyramid_beaker',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_tm',
    'pyramid_webassets',
    'pyramid_zodbconn',
    'pytz',
    'pyzmq',
    'repoze.evolution',
    'requests',
    'transaction',
    'waitress',
]

setup(name='papaye',
      version=VERSION,
      description='A basic PyPi server clone written in Pyramid Web Framework, using ZODB and Beaker Cache.',
      long_description=README + '\n\n' + CHANGES,
      classifiers="""
          Programming Language :: Python
          Programming Language :: Python :: 3.3
          Programming Language :: Python :: 3.4
          Framework :: Pyramid
          Topic :: Internet :: WWW/HTTP
          Topic :: Internet :: WWW/HTTP :: WSGI :: Application
      """,
      author='Romain Commandé',
      author_email='commande.romain@gmail.com',
      url='https://github.com/rcommande/papaye',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='papaye',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = papaye:main
      [console_scripts]
      papaye_init = papaye.scripts.initialize:main
      papaye_evolve = papaye.scripts.evolve:main
      # papaye_worker = papaye.scripts.worker:main
      papaye = papaye.scripts.papaye:main
      """,
      )
