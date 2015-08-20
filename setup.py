#!/usr/bin/env python

from setuptools import setup

setup(name='mhelper',
      version='0.2.0',
      description='MIDAS Helper Utilities',
      author='Matthias W. Smith',
      author_email='mwsmith2@uw.edu',
      py_modules=['midas', 'mhelper'],
      entry_points={
        'console_scripts': [
            'mhelper = mhelper:main'
            ]
        }
     )
