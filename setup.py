from setuptools import setup, find_packages

setup(
    name='pykicad',
    packages=find_packages(),
    version='0.1.1',
    description='Library for working with KiCAD file formats',
    long_description=open('README.md').read(),
    author='David Craven',
    author_email='david@craven.ch',
    url='https://github.com/dvc94ch/pykicad',
    keywords=['kicad', 'file formats', 'parser'],
    install_requires=['pyparsing'],
    tests_require=['pytest'],
    license='ISC'
)
