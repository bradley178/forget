#!/usr/bin/env python -tt
    
try:
    import multiprocessing
except ImportError:
    pass
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["--cov-report", "term-missing", "--cov", "lib/forget", "lib/forget"]
        self.test_suite = True
    def run_tests(self):
        import pytest
        raise SystemExit(pytest.main(self.test_args))
                
setup(name='forget',
      author='Bradley Harris',
      version='0.1',      
      packages=find_packages('lib'),
      package_dir = {'':'lib'},
      scripts=['bin/forgetit'],
      tests_require=["pytest", "pytest-cov", "mock"],
      cmdclass = {'test': PyTest},      
)