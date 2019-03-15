# -*- coding: utf-8 -*-
#
# This file is part of bdsSnmpAdaptor software.
#
# Copyright (C) 2017-2019, RtBrick Inc
# License: BSD License 2.0
#
import os
import sys
import unittest as unittest

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Information Technology
Intended Audience :: System Administrators
Intended Audience :: Telecommunications Industry
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.1
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Communications
Topic :: Software Development :: Libraries :: Python Modules
"""

requires = open('requirements.txt').read()

if sys.version_info[:2] < (2, 6):
    print("ERROR: this package requires Python 2.6 or later!")
    sys.exit(1)

try:
    from setuptools import setup, Command

    params = {
        'install_requires': requires,
        'zip_safe': True
    }

except ImportError:
    for arg in sys.argv:
        if 'egg' in arg:
            print('setuptools is required')
            sys.exit(1)

    from distutils.core import setup, Command

    params = {'requires': requires}

params.update(
    {
        'name': 'bdsSnmpAdaptor',
        'version': open(os.path.join('bdssnmpadaptor', '__init__.py')).read().split('\'')[1],
        'description': 'RtBrock SNMP Adaptor',
        'long_description': 'SNMP interface to the RtBrick system',
        'maintainer': 'Stefan Lieberth <stefan@rtbrick.com',
        'author': 'Stefan Lieberth',
        'author_email': 'stefan@rtbrick.com',
        'url': 'https://github.com/rtbrick/bdsSnmpAdaptor',
        'platforms': ['any'],
        'classifiers': [x for x in classifiers.split('\n') if x],
        'license': 'BSD',
        'packages': ['bdssnmpadaptor',
                     'bdssnmpadaptor.commands',
                     'bdssnmpadaptor.mapping_modules'],
        'entry_points': {
            'console_scripts': [
                'bds-snmp-manager = bdssnmpadaptor.commands.manager:main',
                'bds-snmp-responder = bdssnmpadaptor.commands.responder:main',
                'bds-snmp-notificator = bdssnmpadaptor.commands.notificator:main',
            ]
        }
    }
)


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        suite = unittest.TestLoader().loadTestsFromNames(
            ['tests.__main__.suite']
        )

        unittest.TextTestRunner(verbosity=2).run(suite)


params['cmdclass'] = {
    'test': PyTest,
    'tests': PyTest,
}

setup(**params)
