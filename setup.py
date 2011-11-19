from setuptools import setup

setup(name='pyhub',
      version = '0.1',
      download_url = 'git@github.com:andreif/pyhub.git',
      packages = ['pyhub'],
      author = 'Andrei Fokau',
      author_email = 'andrei.fokau@neutron.kth.se',
      description = '',
      keywords = '',
      url = 'http://github.com/andreif/pyhub',
      license = 'MIT',
      requires = [],
      entry_points = {
          'console_scripts' : ['pyhub = pyhub.pyhub:command']
      }
    )