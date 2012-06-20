# coding=utf-8
"""Python packaging."""
import os
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(name='marmelune.vagrantboxbuilder',
      version=read_relative_file('version.txt').strip(),
      description='Automate creation of Vagrant base boxes',
      long_description=read_relative_file('README.rst'),
      classifiers=['Development Status :: 1 - Planning'
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 2.7',
                   ],
      keywords='VirtualBox Vagrant',
      author='Benoit Bryon',
      author_email='benoit@marmelune.net',
      url='https://github.com/benoitbryon/marmelune.vagrantboxbuilder',
      license='BSD',
      namespace_packages=['marmelune'],
      packages=['marmelune'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
      entry_points={
          'console_scripts': [
              'vagrantboxbuilder = marmelune.vagrantboxbuilder.scripts:main',
          ]
      },
      )