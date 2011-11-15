import os
from setuptools import setup, find_packages
version = '0.5'
README = os.path.join(os.path.dirname(__file__), 'README.txt')
long_description = open(README).read() + 'nn'
setup(name='dmon',
      version=version,
      description=("dissemination monitoring toolbox"),
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        ("Topic :: Util :: Libraries :: Python Modules"),
        ],
      keywords='configuration, resources',
      author='Guillaume Aubert',
      author_email='guillaume.aubert@eumetsat.int',
      url='http://www.eumetsat.int',
      license='Apache 2.0',
      packages=['eumetsat','eumetsat.dmon','eumetsat.dmon.tests'],
      package_dir={'eumetsat':'eumetsat', 'eumetsat.dmon': 'eumetsat/dmon', 'eumetsat.dmon.tests':'eumetsat/dmon/tests'},
      #package_data={'org.ctbto.conf': ['tests/test.config','tests/foo.config','tests/rn.par','tests/rn1.par']},
      #data_files=[('/tmp/py-tests',['/home/aubert/dev/src-reps/java-balivernes/RNpicker/dists/conf-dist/tests/foo.config','/home/aubert/dev/src-reps/java-balivernes/RNpicker/dists/conf-dist/tests/test.config'])],
      install_requires=['Logbook>=0.3', 'colorama>=0.2','requests>=0.7', 'BeautifulSoup>=3.2']
      )
