import os
import os.path
import sys
from pykicad.sexpr import *


MODULE_SEARCH_PATH = 'KISYSMOD'


def find_library(library):
    for path in os.environ.get(MODULE_SEARCH_PATH).split(os.pathsep):
        full_path = os.path.join(path, library + '.pretty')
        if os.path.isdir(full_path):
            return full_path


def find_module(library, module):
    full_name = os.path.join(library + '.pretty', module + '.kicad_mod')
    for path in os.environ.get(MODULE_SEARCH_PATH).split(os.pathsep):
        full_path = os.path.join(path, full_name)
        if os.path.isfile(full_path):
            return full_path


def list_libraries():
    libraries = []
    for path in os.environ.get(MODULE_SEARCH_PATH).split(os.pathsep):
        for lib in os.listdir(path):
            if lib.endswith('.pretty'):
                libraries.append('.'.join(lib.split('.')[0:-1]))
    return libraries


def list_modules(library):
    modules = []
    for file in os.listdir(find_library(library)):
        if file.endswith('.kicad_mod'):
            modules.append('.'.join(file.split('.')[0:-1]))
    return modules


def list_all_modules():
    modules = []
    for lib in list_libraries():
        modules += list_modules(lib)
    return modules


### AST
class Net(AST):
    tag = 'net'
    schema = {
        '0': {
            '_attr': 'code',
            '_parser': integer
        },
        '1': {
            '_attr': 'name',
            '_parser': text
        }
    }

    def __init__(self, code, name):
        super().__init__(code=code, name=name)

class Drill(AST):
    tag = 'drill'
    schema = {
        '0': {
            '_attr': 'size',
            '_parser': number | (Suppress('oval') + number + number),
            '_printer': (lambda size:
                        'oval %s %s' % (str(size[0]), str(size[1])) \
                         if isinstance(size, list) else str(size)),
            '_optional': True
        },
        'offset': {
            '_parser': number + number,
            '_optional': True
        },
    }

    def __init__(self, size, offset=None):
        super().__init__(size=size, offset=offset)


class Pad(AST):
    tag = 'pad'
    schema = {
        '0': {
            '_attr': 'name',
            '_parser': text
        },
        '1': {
            '_attr': 'type',
            '_parser': Literal('smd') | 'thru_hole' | 'np_thru_hole' | 'connect'
        },
        '2': {
            '_attr': 'shape',
            '_parser': Literal('circle') | 'rect' | 'oval' | 'trapezoid'
        },
        'at': number + number + Optional(number),
        'size': number + number,
        'layers': {
            '_parser': Group(OneOrMore(text)).setParseAction(lambda x: [list(x[0])]),
        },
        'drill': {
            '_parser': Drill,
            '_printer': Drill.to_string,
            '_optional': True
        },
        'rect_delta': {
            '_parser': number + number,
            '_optional': True
        },
        'solder_mask_margin': {
            '_parser': number,
            '_optional': True
        },
        'solder_paste_margin': {
            '_parser': number,
            '_optional': True
        },
        'solder_paste_margin_ratio': {
            '_parser': number,
            '_optional': True
        },
        'clearance': {
            '_parser': number,
            '_optional': True
        },
        'zone_connect': {
            '_parser': number,
            '_optional': True
        },
        'net': {
            '_parser': Net,
            '_printer': Net.to_string,
            '_optional': True
        }
    }

    def __init__(self, name, type, shape, at, size, layers,
                 drill=None, rect_delta=None, clearance=None,
                 zone_connect=None, solder_mask_margin=None,
                 solder_paste_margin=None, solder_paste_margin_ratio=None,
                 net=None):

        super().__init__(name=name, type=type, shape=shape, at=at, size=size,
                         layers=layers, drill=drill, rect_delta=rect_delta,
                         clearance=clearance, net=net,
                         zone_connect=zone_connect,
                         solder_mask_margin=solder_mask_margin,
                         solder_paste_margin=solder_paste_margin,
                         solder_paste_margin_ratio=solder_paste_margin_ratio)


class Text(AST):
    tag = 'fp_text'
    schema = {
        '0': {
            '_attr': 'prop',
            '_parser': text
        },
        '1': {
            '_attr': 'value',
            '_parser': text
        },
        '2': {
            '_tag': 'at',
            '_parser': number + number + Optional(number)
        },
        'layer': text,
        'effects': {
            'font': {
                'size': {
                    '_parser': number + number,
                    '_optional': True
                },
                'thickness': {
                    '_parser': number,
                    '_optional': True
                },
                '_optional': True
            },
            'justify': {
                '_parser': text,
                '_optional': True
            },
            '_optional': True
        },
        'hide': {
            '_parser': Literal('hide').setParseAction(lambda x: True),
            '_printer': lambda hide: 'hide' if hide else '',
            '_optional': True,
            '_tag': False,
            '_attr': 'hide'
        }
    }

    def __init__(self, prop, value, at, layer, hide=False, size=None,
                 thickness=None, justify=None):

        super().__init__(prop=prop, value=value, at=at, layer=layer,
                         hide=hide, size=size, thickness=thickness,
                         justify=justify)


class Line(AST):
    tag = 'fp_line'
    schema = {
        '0': {
            '_tag': 'start',
            '_parser': number + number
        },
        '1': {
            '_tag': 'end',
            '_parser': number + number
        },
        'layer': text,
        'width': {
            '_parser': number,
            '_optional': True
        }
    }

    def __init__(self, start, end, layer, width=None):
        super().__init__(start=start, end=end, layer=layer, width=width)


class Circle(AST):
    tag = 'fp_circle'
    schema = {
        '0': {
            '_tag': 'center',
            '_parser': number + number
        },
        '1': {
            '_tag': 'end',
            '_parser': number + number
        },
        'layer': text,
        'width': {
            '_parser': number,
            '_optional': True
        }
    }

    def __init__(self, center, end, layer, width=None):
        super().__init__(center=center, end=end, layer=layer, width=width)


class Arc(AST):
    tag = 'fp_arc'
    schema = {
        '0': {
            '_tag': 'start',
            '_parser': number + number
        },
        '1': {
            '_tag': 'end',
            '_parser': number + number
        },
        '2': {
            '_tag': 'angle',
            '_parser': number
        },
        'layer': text,
        'width': {
            '_parser': number,
            '_optional': True
        }
    }

    def __init__(self, start, end, angle, layer, width=None):
        super().__init__(start=start, end=end, angle=angle,
                         layer=layer, width=width)


class Model(AST):
    tag = 'model'
    schema = {
        '0': {
            '_attr': 'path',
            '_parser': text
        },
        'at': {
            'xyz': number + number + number,
            '_attr': 'at'
        },
        'scale': {
            'xyz': number + number + number,
            '_attr': 'scale'
        },
        'rotate': {
            'xyz': number + number + number,
            '_attr': 'rotate'
        }
    }

    def __init__(self, path, at, scale, rotate):
        super().__init__(path=path, at=at, scale=scale, rotate=rotate)


class Module(AST):
    tag = 'module'
    schema = {
        '0': {
            '_attr': 'name',
            '_parser': text
        },
        'layer': text,
        'descr': {
            '_parser': text,
            '_optional': True
        },
        'tags': {
            '_parser': text,
            '_optional': True
        },
        'attr': {
            '_parser': text,
            '_optional': True
        },
        'at': {
            '_parser': number + number + Optional(number),
            '_optional': True
        },
        'tedit': {
            '_parser': text,
            '_optional': True
        },
        'tstamp': {
            '_parser': text,
            '_optional': True
        },
        'solder_mask_margin': {
            '_parser': number,
            '_optional': True
        },
        'model': {
            '_parser': Model,
            '_printer': Model.to_string,
            '_optional': True
        },
        'pads': {
            '_parser': Pad,
            '_printer': Pad.to_string,
            '_multiple': True
        },
        'texts': {
            '_parser': Text,
            '_printer': Text.to_string,
            '_multiple': True
        },
        'lines': {
            '_parser': Line,
            '_printer': Line.to_string,
            '_multiple': True
        },
        'circles': {
            '_parser': Circle,
            '_printer': Circle.to_string,
            '_multiple': True
        },
        'arcs': {
            '_parser': Arc,
            '_printer': Arc.to_string,
            '_multiple': True
        }
    }

    def __init__(self, name, layer, descr=None, tags=None, attr=None, at=None,
                 tedit=None, tstamp=None, solder_mask_margin=None, model=None,
                 pads=[], lines=[], texts=[], circles=[], arcs=[]):

        if not isinstance(pads, list):
            pads = [pads]
        if not isinstance(lines, list):
            lines = [lines]
        if not isinstance(texts, list):
            texts = [texts]
        if not isinstance(circles, list):
            circles = [circles]
        if not isinstance(arcs, list):
            arcs = [arcs]

        super().__init__(name=name, layer=layer, descr=descr, tags=tags,
                         solder_mask_margin=solder_mask_margin,
                         attr=attr, at=at, model=model, pads=pads, texts=texts,
                         lines=lines, circles=circles, arcs=arcs)


    @classmethod
    def from_file(cls, path):
        module = open(path, 'r', encoding='utf-8').read()
        return cls.parse(module)

    @classmethod
    def from_library(cls, lib, name):
        return cls.from_file(find_module(lib, name))
