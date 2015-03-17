import os
from setuptools import setup, find_packages
version = '0.5'
README = os.path.join(os.path.dirname(__file__), 'README.txt')
long_description = open(README).read() + 'nn'
setup(name='diss_player',
      version=version,
      description=("dissemination player"),
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
      packages=['eumetsat','eumetsat.dmon', 'eumetsat.dmon.common', 'eumetsat.dmon.dissplayer', 'eumetsat.dmon.parsers', 'eumetsat.dmon.tests'],
      package_dir={'eumetsat':'eumetsat', 'eumetsat.dmon': 'eumetsat/dmon', 'eumetsat.dmon.common': 'eumetsat/dmon/common', 'eumetsat.dmon.dissplayer': 'eumetsat/dmon/dissplayer', 'eumetsat.dmon.parsers': 'eumetsat/dmon/parsers', 'eumetsat.dmon.tests': 'eumetsat/dmon/tests'},
      #package_data={'org.ctbto.conf': ['tests/test.config','tests/foo.config','tests/rn.par','tests/rn1.par']},
      #data_files=[('/tmp/py-tests',['/home/aubert/dev/src-reps/java-balivernes/RNpicker/dists/conf-dist/tests/foo.config','/home/aubert/dev/src-reps/java-balivernes/RNpicker/dists/conf-dist/tests/test.config'])],
      install_requires=['pytz>=2014.10', 'APScheduler>=3.0.2', 'six>=1.9.0']
      )
