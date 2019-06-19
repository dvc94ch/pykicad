import os
import os.path
import re
import sys
from io import open
from pykicad.sexpr import *

MODULE_SEARCH_PATH = "PYKICAD_MOD_PATH"

###########################
# Utility methods         #
###########################
def find_library(library):
    '''Returns full path of specified library'''
    for path in os.environ.get(MODULE_SEARCH_PATH).split(os.pathsep):
        full_path = os.path.join(path, library + '.pretty')
        if os.path.isdir(full_path):
            return full_path

def find_module(library, module):
    '''Returns full path of specified module'''
    full_name = os.path.join(library + '.pretty', module + '.kicad_mod')
    for path in os.environ.get(MODULE_SEARCH_PATH).split(os.pathsep):
        full_path = os.path.join(path, full_name)
        if os.path.isfile(full_path):
            return full_path

def list_libraries():
    '''Returns all footprint libraries'''
    libraries = []
    for path in os.environ.get(MODULE_SEARCH_PATH).split(os.pathsep):
        for lib in os.listdir(path):
            if lib.endswith('.pretty'):
                libraries.append('.'.join(lib.split('.')[0:-1]))
    return libraries

def list_modules(library):
    '''Returns all modules in specific library'''
    modules = []
    for file in os.listdir(find_library(library)):
        if file.endswith('.kicad_mod'):
            modules.append('.'.join(file.split('.')[0:-1]))
    return modules

def filter_by_regex(alist, regex):
    '''Filter a list of strings using a regular expression'''
    regex = re.compile(regex)
    return [x for x in alist if regex.match(x)]

def list_all_modules():
    '''Returns all modules in all libraries'''
    modules = []
    for lib in list_libraries():
        modules += list_modules(lib)
    return modules

def flip_layer(layer):
    '''
    Flips from front to back layer
    Returns nothing if not on front or back layer
    '''
    if filter_by_regex([layer],"^[FB].[a-zA-Z]{1,}$"):
        side, layer = layer.split('.')
        side = 'B' if side == 'F' else 'B'
        return side + '.' + layer
