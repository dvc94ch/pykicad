import os
import os.path
import re
import sys
from io import open
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

def filter_by_regex(alist, regex):
    regex = re.compile(regex)
    return [x for x in alist if regex.match(x)]

def list_all_modules():
    modules = []
    for lib in list_libraries():
        modules += list_modules(lib)
    return modules


def flip_layer(layer):
    side, layer = layer.split('.')
    side = 'B' if side == 'F' else 'B'
    return side + '.' + layer


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
                 layers=None, net=None, die_length=None, solder_mask_margin=None,
                 solder_paste_margin=None, solder_paste_margin_ratio=None,
                 clearance=None, zone_connect=None):

        at = self.init_list(at, [0, 0])
        layers = self.init_list(layers, ['F.Cu'])

        super(Pad, self).__init__(name=name, type=type, shape=shape, size=size,
                                  at=at, rect_delta=rect_delta,
                                  roundrect_rratio=roundrect_rratio,
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

    def rotate(self, angle):
        '''Rotates a pad by an angle.'''

        if len(self.at) > 2:
            self.at[2] += angle
        else:
            self.at.append(angle)

    def flip(self):
        '''Flip a pad.'''

        self.layers = [flip_layer(layer) for layer in self.layers]
        self.at[1] = -self.at[1]
        if len(self.at) > 2:
            self.at[2] = -self.at[2]

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

    def rotate(self, angle):
        '''Rotates a textual element by an angle.'''

        if len(self.at) > 2:
            self.at[2] += angle
        else:
            self.at.append(angle)

    def flip(self):
        '''Flip a textual element.'''

        self.layer = flip_layer(self.layer)
        self.at[1] = -self.at[1]
        self.justify = 'mirror' if not self.justify == 'mirror' else None


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

    def flip(self):
        '''Flip a line.'''

        self.layer = flip_layer(self.layer)
        self.start[1] = -self.start[1]
        self.end[1] = -self.end[1]


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
        super(Circle, self).__init__(center=center, end=end, layer=layer,
                                     width=width)

    def flip(self):
        '''Flip a circle.'''

        self.layer = flip_layer(self.layer)


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

    def flip(self):
        '''Flip an arc.'''

        self.layer = flip_layer(self.layer)
        raise NotImplementedError()


class Model(AST):
    tag = 'model'
    schema = {
        '0': {
            '_parser': text,
            '_attr': 'path'
        },
        'at': {
            'xyz': {
                '_parser': number + number + number,
                '_attr': 'at'
            }
        },
        'scale': {
            'xyz': {
                '_parser': number + number + number,
                '_attr': 'scale'
            }
        },
        'rotate': {
            'xyz': {
                '_parser': number + number + number,
                '_attr': 'rotate'
            }
        }
    }

    def __init__(self, path, at, scale, rotate):
        super(Model, self).__init__(path=path, at=at, scale=scale, rotate=rotate)


class Module(AST):
    tag = 'module'
    schema = {
        '0': {
            '_parser': text,
            '_attr': 'name'
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
        # default: Add module to BOM
        # smd: Add module to BOM and SMT placement file
        # virtual: Don't add module to BOM
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
        'model': {
            '_parser': Model,
            '_multiple': True
        }
    }

    def __init__(self, name, version=None, locked=False, placed=False,
                 layer='F.Cu', tedit=None, tstamp=None, at=None,
                 descr=None, tags=None, path=None, attr=None,
                 autoplace_cost90=None, autoplace_cost180=None,
                 solder_mask_margin=None, solder_paste_margin=None,
                 solder_paste_ratio=None, clearance=None,
                 zone_connect=None, thermal_width=None, thermal_gap=None,
                 texts=None, lines=None, circles=None, arcs=None, curves=None,
                 polygons=None, pads=None, model=None):

        at = self.init_list(at, [0, 0])
        pads = self.init_list(pads, [])
        texts = self.init_list(texts, [])
        lines = self.init_list(lines, [])
        circles = self.init_list(circles, [])
        arcs = self.init_list(arcs, [])
        curves = self.init_list(curves, [])
        polygons = self.init_list(polygons, [])

        super(Module, self).__init__(name=name, version=version, locked=locked,
                                     placed=placed, layer=layer, tedit=tedit,
                                     tstamp=tstamp, at=at, descr=descr,
                                     tags=tags, path=path, attr=attr,
                                     autoplace_cost90=autoplace_cost90,
                                     autoplace_cost180=autoplace_cost180,
                                     solder_mask_margin=solder_mask_margin,
                                     solder_paste_margin=solder_paste_margin,
                                     solder_paste_ratio=solder_paste_ratio,
                                     clearance=clearance, zone_connect=zone_connect,
                                     thermal_width=thermal_width, thermal_gap=thermal_gap,
                                     texts=texts, lines=lines, circles=circles,
                                     arcs=arcs, curves=curves, polygons=polygons,
                                     pads=pads, model=model)

    def pads_by_name(self, name):
        '''Returns a list of pads.
        The pads in the list may be in an arbitrary order, or be
        non-consecutive. Multiple pads can have the same name.'''

        pads = []
        for pad in self.pads:
            if pad.name == name:
                pads.append(pad)
        return pads

    def set_reference(self, name):
        '''Change the reference/identifier of a module.
        Aside from changing the name, we also need to update the
        textual elements of type 'reference'.'''

        self.name = name
        for text in self.texts:
            if text.type == 'reference':
                text.text = name

    def set_value(self, value):
        '''Change the value of a module.
        Updates all textual elements of type 'value'.'''

        for text in self.texts:
            if text.type == 'value':
                text.text = value

    def geometry(self):
        for element_list in [self.lines, self.circles, self.arcs,
                             self.curves, self.polygons]:
            for elem in element_list:
                yield elem

    def elements_by_layer(self, layer):
        '''Returns a iterator of elements on layer.'''

        for elem in self.geometry():
            if elem.layer == layer:
                yield elem

    def courtyard(self):
        '''Returns the courtyard elements of a module.'''

        return list(self.elements_by_layer(self.layer.split('.')[0] + '.CrtYd'))

    def place(self, x, y):
        '''Sets the x and y coordinates of the module.'''

        self.at[0] = x
        self.at[1] = y

    def rotate(self, angle):
        '''Rotates the module by an angle.
        Also applies rotation to all text elements and pads.'''

        if len(self.at) > 2:
            self.at[2] += angle
        else:
            self.at.append(angle)

        for pad in self.pads:
            pad.rotate(angle)

        for text in self.texts:
            text.rotate(angle)

    def connect(self, pad, net):
        '''Sets the net on all pads called :data:pad.'''

        for pad in self.pads_by_name(pad):
            pad.net = net

    def flip(self):
        self.layer = flip_layer(self.layer)
        for pad in self.pads:
            pad.flip()
        for text in self.texts:
            text.flip()
        for elem in self.geometry():
            elem.flip()

    @classmethod
    def from_file(cls, path):
        module = open(path, 'r', encoding='utf-8').read()
        return cls.parse(module)

    @classmethod
    def from_library(cls, lib, name):
        return cls.from_file(find_module(lib, name))
