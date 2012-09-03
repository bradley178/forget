#!/usr/bin/env python -tt
from setuptools import setup, find_packages
                
setup(name='forget',
      author='Bradley Harris',
      version='0.1',      
      packages=find_packages('lib'),
      package_dir = {'':'lib'},
      scripts=['bin/forgetit'],
)