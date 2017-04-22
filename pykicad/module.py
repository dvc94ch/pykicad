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
    counter = 1

    def __init__(self, name='', code=None):
        if code is None:
            code = Net.counter
            Net.counter += 1

        super(Net, self).__init__(code=code, name=name)

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
        'offset': number + number,
    }

    def __init__(self, size, offset=None):
        super(Drill, self).__init__(size=size, offset=offset)


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
            '_parser': Literal('circle') | 'rect' | 'roundrect' | 'oval' | 'trapezoid'
        },
        'size': number + number,
        'at': number + number + Optional(number),
        'rect_delta': number + number,
        'roundrect_rratio': number,
        'drill': Drill,
        'layers': Group(OneOrMore(text)).setParseAction(lambda x: [list(x[0])]),
        'net': Net,
        'die_length': number,
        'solder_mask_margin': number,
        'solder_paste_margin': number,
        'solder_paste_margin_ratio': number,
        'clearance': number,
        'zone_connect': integer
    }

    def __init__(self, name, type='smd', shape='rect', size=None, at=None,
                 rect_delta=None, roundrect_rratio=None, drill=None,
                 layers=['F.Cu'], net=None, die_length=None, solder_mask_margin=None,
                 solder_paste_margin=None, solder_paste_margin_ratio=None,
                 clearance=None, zone_connect=None):


        super(Pad, self).__init__(name=name, type=type, shape=shape, size=size, at=at,
                                  rect_delta=rect_delta, roundrect_rratio=roundrect_rratio,
                                  layers=layers, drill=drill, clearance=clearance,
                                  net=net, die_length=die_length,
                                  solder_mask_margin=solder_mask_margin,
                                  solder_paste_margin=solder_paste_margin,
                                  solder_paste_margin_ratio=solder_paste_margin_ratio,
                                  zone_connect=zone_connect)

    def is_valid(self):
        if self.shape == 'trapezoid' and self.rect_delta is None:
            return False

        if self.shape == 'roundrect' and self.roundrect_rratio is None:
            return False

        if self.shape == 'thru_hole' or self.shape == 'np_thru_hole':
            if self.drill is None:
                return False

        return True


class Text(AST):
    tag = 'fp_text'
    schema = {
        '0': {
            '_attr': 'type',
            '_parser': Literal('reference') | 'value' | 'user'
        },
        '1': {
            '_attr': 'text',
            '_parser': text
        },
        '2': {
            '_tag': 'at',
            '_parser': number + number + Optional(number)
        },
        'layer': text,
        'effects': {
            'font': {
                'size': number + number,
                'thickness': number,
                'bold': flag('bold'),
                'italic': flag('italic')
            },
            'justify': Literal('left') | 'right' | 'top' | 'bottom' | 'mirror',
            'hide': flag('hide')
        },
        'hide': flag('hide')
    }

    def __init__(self, type='user', text='**', at=None, layer='F.SilkS',
                 size=None, thickness=None, bold=False, italic=False,
                 justify=None, hide=False):

        super(Text, self).__init__(type=type, text=text, at=at, layer=layer,
                                   size=size, thickness=thickness, bold=bold,
                                   italic=italic, justify=justify, hide=hide)


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
        'width': number
    }

    def __init__(self, start, end, layer='F.SilkS', width=None):
        super(Line, self).__init__(start=start, end=end, layer=layer, width=width)


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
        'width': number
    }

    def __init__(self, center, end, layer='F.SilkS', width=None):
        super(Circle, self).__init__(center=center, end=end, layer=layer, width=width)


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
        'width': number
    }

    def __init__(self, start, end, angle, layer='F.SilkS', width=None):
        super(Arc, self).__init__(start=start, end=end, angle=angle,
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
        super(Model, self).__init__(path=path, at=at, scale=scale, rotate=rotate)


class Module(AST):
    tag = 'module'
    schema = {
        '0': {
            '_attr': 'name',
            '_parser': text
        },
        'version': integer,
        'locked': flag('locked'),
        'placed': flag('placed'),
        'layer': Literal('F.Cu') | 'B.Cu',
        'tedit': hex,
        'tstamp': hex,
        'at': number + number + Optional(number),
        'descr': text,
        'tags': text,
        'path': text,
        'attr': Literal('smd') | 'virtual',
        'autoplace_cost90': integer,
        'autoplace_cost180': integer,
        'solder_mask_margin': number,
        'solder_paste_margin': number,
        'solder_paste_ratio': number,
        'clearance': number,
        'zone_connect': integer,
        'thermal_width': number,
        'thermal_gap': number,
        'texts': {
            '_parser': Text,
            '_multiple': True
        },
        'lines': {
            '_parser': Line,
            '_multiple': True
        },
        'circles': {
            '_parser': Circle,
            '_multiple': True
        },
        'arcs': {
            '_parser': Arc,
            '_multiple': True
        },
        'pads': {
            '_parser': Pad,
            '_multiple': True
        },
        'model': Model
    }

    def __init__(self, name, version=None, locked=False, placed=False,
                 layer='F.Cu', tedit=None, tstamp=None, at=None,
                 descr=None, tags=None, path=None, attr=None,
                 autoplace_cost90=None, autoplace_cost180=None,
                 solder_mask_margin=None, solder_paste_margin=None,
                 solder_paste_ratio=None, clearance=None,
                 zone_connect=None, thermal_width=None, thermal_gap=None,
                 texts=[], lines=[], circles=[], arcs=[], curves=[], polygons=[],
                 pads=[], model=None):

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

        super(Module, self).__init__(name=name, version=version, locked=locked, placed=placed,
                                     layer=layer, tedit=tedit, tstamp=tstamp,
                                     at=at, descr=descr, tags=tags, path=path, attr=attr,
                                     autoplace_cost90=autoplace_cost90,
                                     autoplace_cost180=autoplace_cost180,
                                     solder_mask_margin=solder_mask_margin,
                                     solder_paste_margin=solder_paste_margin,
                                     solder_paste_ratio=solder_paste_ratio,
                                     clearance=clearance, zone_connect=zone_connect,
                                     thermal_width=thermal_width, thermal_gap=thermal_gap,
                                     texts=texts, lines=lines, circles=circles, arcs=arcs,
                                     curves=curves, polygons=polygons, pads=pads, model=model)


    @classmethod
    def from_file(cls, path):
        module = open(path, 'r').read().decode('utf-8')
        return cls.parse(module)

    @classmethod
    def from_library(cls, lib, name):
        return cls.from_file(find_module(lib, name))
