#-*- coding:utf-8 -*-
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'CodernityDB',
    'pyramid',
    'pyramid_beaker',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_tm',
    'requests',
    'transaction',
    'waitress',
    'pyzmq',
]

setup(name='papaye',
      version='0.0',
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
