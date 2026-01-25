from setuptools import setup, find_packages
import versioneer


with open('README.md') as file:
    readme = file.read()


setup(
    name='pykicad',
    packages=find_packages(),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Library for working with KiCAD file formats',
    long_description=readme,
    author='David Craven',
    author_email='david@craven.ch',
    url='https://github.com/dvc94ch/pykicad',
    keywords=['kicad', 'file formats', 'parser'],
    install_requires=['pyparsing'],
    tests_require=['pytest'],
    python_requires='>=3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    license='ISC',
    zip_safe=False,
)
