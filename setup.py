from setuptools import setup
import setuptools

import pyicub

setup(name='pyicub',
      version=pyicub.__version__,
      description=pyicub.__description__,
      url='http://github.com/s4hri/pyicub',
      author=pyicub.__authors__,
      author_email=pyicub.__emails__,
      license=pyicub.__license__,
      packages=setuptools.find_packages(),
      zip_safe=False)