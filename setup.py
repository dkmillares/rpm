#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from rudix import VERSION

with open('README') as f:
    README = f.read()

setup(name='rudix',
      version=VERSION,
      license='BSD',
      description='Rudix Package Manager',
      long_description=README,
      author='Rudá Moura',
      author_email='ruda.moura@gmail.com',
      url='http://rudix.org/',
      keywords='package manager',
      classifiers = ["Programming Language :: Python",
                     "License :: OSI Approved :: BSD License",
                     "Environment :: MacOS X",
                     "Operating System :: MacOS :: MacOS X",
                     "Topic :: System :: Installation/Setup",
                     "Topic :: System :: Software Distribution"],
      packages=find_packages(),
      entry_points={'console_scripts': ['rudix = rudix.main:main']}
)
