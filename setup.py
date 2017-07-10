from distutils.core import setup

setup(
    name='pykicad',
    packages=['pykicad'],
    version='0.0.4',
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
