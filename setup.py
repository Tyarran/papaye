# -*- coding:utf-8 -*-
import os
import papaye

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
VERSION = papaye.__version__

requires = [
    'filemagic',
    'pyramid',
    'pyramid_beaker',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_tm',
    'pyramid_zodbconn',
    'pyzmq',
    'requests',
    'transaction',
    'waitress',
]

setup(name='papaye',
      version=VERSION,
      description='papaye',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Romain Commandé',
      author_email='commande.romain@gmail.com',
      maintainer='Moi moi et remoi',
      url='http://www.rcommande.org',
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
      papaye_worker = papaye.scripts.worker:main
      """,
      )
