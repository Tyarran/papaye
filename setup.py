# -*- coding:utf-8 -*-
import os
import pip

from os.path import join
from setuptools import setup, find_packages


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(join(HERE, 'README.rst')).read()
CHANGES = open(join(HERE, 'CHANGES.txt')).read()
# REQUIREMENTS_DIR = join(HERE, 'requirements')
# REQUIREMENTS_FILE = join(REQUIREMENTS_DIR, 'requirements.txt')
# REQUIREMENTS_DEV_FILE = join(REQUIREMENTS_DIR, 'requirements-dev.txt')
VERSION = '0.2.2'


# dependency_gen = pip.req.parse_requirements(REQUIREMENTS_FILE, session=False)
# REQUIREMENTS = [str(ir.req) for ir in dependency_gen]

# dependency_gen = pip.req.parse_requirements(
#     REQUIREMENTS_DEV_FILE, session=False,
# )
# REQUIREMENTS_DEV = [str(ir.req) for ir in dependency_gen]


setup(name='papaye',
      version=VERSION,
      description='Yet another Python Package repository (local PyPI)',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Framework :: Pyramid',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      ],
      author='Romain Commandé',
      author_email='commande.romain@gmail.com',
      url='https://github.com/rcommande/papaye',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='papaye',
    #   install_requires=REQUIREMENTS,
    #   extras_require={
    #       'dev': REQUIREMENTS_DEV,
    #   },
      entry_points="""\
      [paste.app_factory]
      main = papaye:main
      [console_scripts]
      papaye_init = papaye.scripts.initialize:main
      papaye_evolve = papaye.scripts.evolve:main
      papaye_worker = papaye.scripts.papaye:main
      """,
      )
