#!/usr/bin/env python3.6

# Copyright (c) 2018 by Stefan Lieberth <stefan@lieberth.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Stefan Lieberth - initial implementation, API, and documentation

""" aioRunbook for automated test execution

aioRunbook is a Python package providing a framework for automated network tests and network migrations. 

"""

from os import path
from setuptools import setup, find_packages

base_dir = path.abspath(path.dirname(__file__))

print ("base_dir: {}".format(base_dir))

doclines = __doc__.split('\n', 1)

with open(path.join(base_dir, 'README.rst')) as desc:
    long_description = desc.read()

with open(path.join(base_dir, 'version.py')) as version:
    exec(version.read())

#aiohttp-session-2.3.0

setup(name = 'aioRunbook',
      version = __version__,
      author = __author__,
      author_email = __author_email__,
      url = __url__,
      license = 'Eclipse Public License v1.0',
      description = doclines[0],
      long_description = long_description,
      platforms = 'Any',
      install_requires = ['asyncssh >= 1.0','aiohttp>=2.3.10','PyYAML>=3.12','jtextfsm>=0.3.1',
                          'Jinja2>=2.10','pysnmp>=4.4.4','ncclient>=0.5.3','aiohttp-jinja2>=0.16.0'],
      extras_require = {},
      packages = find_packages(),
      scripts = [],
      test_suite = 'tests',
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet',
          'Topic :: Security :: Cryptography',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Networking'])