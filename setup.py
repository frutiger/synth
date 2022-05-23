from setuptools import setup

setup(name='synth',
      version='0.1.2',
      description='Simulate a monorepo in a polyrepo world',
      url='https://github.com/frutiger/synth',
      author='Masud Rahman',
      license='MIT',
      packages=['synth'],
      entry_points={
          'console_scripts': ['synth=synth.__main__:main'],
      })

