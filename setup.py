#!/usr/bin/env python -tt
from setuptools import setup
                
setup(name='forget',
      author='Bradley Harris',
      version='0.1',      
      packages=['lib/evernote', 'lib/thrift', 'lib/forget'],
      scripts=['bin/forgetit'],
)