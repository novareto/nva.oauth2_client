from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='nva.oauth2_client',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['nva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'grok',
          'setuptools',
          'uvc.api',
          'python-oauth2',
          'zope.app.appsetup',
          # -*- Extra requirements: -*-
      ],
      entry_points={
      }
      )
