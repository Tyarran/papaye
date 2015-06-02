# -*- coding:utf-8 -*-
import os

from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.txt')).read()
VERSION = '0.2.0-dev'

requires = [
    'colander==1.0b1',
    'cornice==1.0.0',
    'cssmin==0.2.0',
    'docutils==0.12',
    'filemagic==1.6',
    'jsmin==2.1.1',
    'pyramid==1.5.7',
    'pyramid_beaker==0.8',
    'pyramid_debugtoolbar==2.3',
    'pyramid_jinja2==2.5',
    'pyramid_tm==0.11',
    'pyramid_webassets==0.9',
    'pyramid_zodbconn==0.7',
    'pytz==2015.2',
    'pyzmq==14.6.0',
    'repoze.evolution==0.6',
    'requests==2.7.0',
    'termcolor==1.1.0',
    'transaction==1.4.4',
    'waitress==0.8.9',
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
      papaye_worker = papaye.scripts.papaye:main
      """,
      )
