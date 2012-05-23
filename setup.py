from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='spreedly-core-python',
      version=version,
      description="A python library to communicate with the Spreedly Core API",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Martin Hult\xc3\xa9n-Ashauer',
      author_email='martin@mooball.com',
      url='http://www.mooball.com',
      license='ZPL',
      py_modules = ['spreedlycore'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
