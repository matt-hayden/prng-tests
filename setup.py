import os, os.path
from setuptools import find_packages, setup

setup(name='PyWordlist',
      version = "1.0",
      description='Passphrase encoding using memorable words',
      url='https://github.com/matt-hayden/prng-tests',
      maintainer="Matt Hayden (Valenceo, LTD.)",
      maintainer_email="github.com/matt-hayden",
      license='Unlicense',
      packages=find_packages(exclude='contrib docs examples lib tests'.split()),
      entry_points = {
          'console_scripts': [
              'chbs=wordlist.cli:main',
              ]
          },
      package_data = {
          'wordlist': ['etc/*', 'lib/*'],
          },
      install_requires = [ 'docopt' ],
      zip_safe=True,
     )
