from setuptools import setup, find_packages
import versioneer

setup(
    name='pykicad',
    packages=find_packages(),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
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
