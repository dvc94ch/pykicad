import os
import os.path
import sys
from pyparsing import *

MODULE_SEARCH_PATH = 'KISYSMOD'

unicodePrintables = u''.join(chr(c) for c in range(sys.maxunicode)
                             if not chr(c) in ' )')
name = Word(unicodePrintables)
text = dblQuotedString | name
number = Combine(Optional('-') + Word(nums) + Optional(Word('.') + Word(nums)))

dblQuotedString.setParseAction(removeQuotes)
number.setParseAction(lambda tokens: float(tokens[0]))


class Tag(object):
    def __init__(self, tag, *args):
        self.tag = tag
        self.args = args

    def __getitem__(self, tag):
        if isinstance(tag, str):
            children = []
            for arg in self.args:
                if isinstance(arg, Tag) and arg.tag == tag:
                    children.append(arg)
            if len(children) < 1:
                return None
            if len(children) < 2 and \
               tag not in ['fp_text', 'fp_line', 'fp_circle', 'fp_arc', 'pad']:
                return children[0]
            return children
        elif isinstance(tag, int):
            return self.args[tag]

    def value(self):
        if len(self.args) < 2:
            return self.args[0]
        return self.args

    @staticmethod
    def parser(name, *args):
        def to_tag(tokens):
            return [Tag(token[0], *token[1:]) for token in tokens]

        parser = Suppress('(') + Literal(name)
        for arg in args:
            parser += arg
        parser = Group(parser + Suppress(')'))
        parser.setResultsName(name)
        parser.setParseAction(to_tag)
        return parser

    @staticmethod
    def suppress(name, *args):
        return Suppress(Optional(Tag.parser(name, *args)))

    def __repr__(self):
        args = []
        for arg in self.args:
            if isinstance(arg, str):
                for char in arg:
                    if char in ' ()':
                        args.append('"%s"' % arg)
                        break
                else:
                    args.append(arg)
            else:
                args.append(repr(arg))
        string = ' '.join(args)
        if string.endswith('\n'):
            string = string[0:-1]
        return '(%s %s)\n' % (self.tag, string)


class Model(object):
    def __init__(self, path, at=[0, 0, 0], scale=[0, 0, 0], rotate=[0, 0, 0]):
        self.path = path
        self.at = at
        self.scale = scale
        self.rotate = rotate

    @staticmethod
    def parser():
        xyz = Tag.parser('xyz', number, number, number)
        return Tag.parser('model', text,
                          Tag.parser('at', xyz) &
                          Tag.parser('scale', xyz) &
                          Tag.parser('rotate', xyz))

    def to_tag(self):
        return Tag('model', self.path,
                   Tag('at', Tag('xyz', *self.at)),
                   Tag('scale', Tag('xyz', *self.scale)),
                   Tag('rotate', Tag('xyz', *self.rotate)))

    @classmethod
    def from_tag(cls, tag):
        assert tag.tag == 'model'
        return cls(tag[0],
                   at=tag['at']['xyz'].value(),
                   scale=tag['scale']['xyz'].value(),
                   rotate=tag['rotate']['xyz'].value())

    def __str__(self):
        return 'Model: %s\n' % repr(self.to_tag())

    def __repr__(self):
        return repr(self.to_tag())


class Drill(object):
    def __init__(self, size=0.8, offset=None):
        self.size = size
        self.offset = offset

    def is_oval(self):
        if isinstance(self.size, float):
            return False
        if isinstance(self.size, list):
            return True

    def has_offset(self):
        if self.offset is None:
            return False
        return True

    @staticmethod
    def parser():
        return Tag.parser('drill', number | ('oval' + number + number),
                          Optional(Tag.parser('offset', number, number)))

    def to_tag(self):
        if self.is_oval():
            hole = ['oval'] + self.size
        else:
            hole = [self.size]

        if self.has_offset():
            offset = [Tag('offset', *self.offset)]
        else:
            offset = []

        return Tag('drill', *(hole + offset))

    @classmethod
    def from_tag(cls, tag):
        assert tag.tag == 'drill'

        if tag[0] == 'oval':
            size = [tag[1], tag[2]]
        else:
            size = tag[0]

        if tag['offset'] is None:
            offset = None
        else:
            offset = tag['offset'].value()

        return cls(size=size, offset=offset)

    def __str__(self):
        return 'Drill: %s\n' % repr(self.to_tag())

    def __repr__(self):
        return repr(self.to_tag())


class Pad(object):
    def __init__(self, name, type='smd', shape='rect', drill=None,
                 at=[0, 0], size=[1, 1], rect_delta=None, layers=['F.Cu']):
        self.name = name
        self.type = type
        self.shape = shape
        self.drill = drill
        self.at = at
        self.size = size
        self.rect_delta = rect_delta
        self.layers = layers

    @staticmethod
    def parser():
        return Tag.parser('pad', name,
                          Literal('smd') | 'thru_hole' | 'np_thru_hole' | 'connect',
                          Literal('circle') | 'rect' | 'oval' | 'trapezoid',
                          Tag.parser('at', number, number,
                                     # Bug in some package definitions?
                                     Suppress(Optional(number))) &
                          Tag.parser('size', number, number) &
                          Tag.parser('layers', OneOrMore(name)) &
                          Optional(Drill.parser()) &
                          # Used when the pad shape is trapezoid
                          Optional(Tag.parser('rect_delta', number, number)) &
                          # Currently only applied to few components, of limited
                          # use
                          Tag.suppress('solder_paste_margin_ratio', number) &
                          Tag.suppress('solder_paste_margin', number) &
                          Tag.suppress('solder_mask_margin', number) &
                          Tag.suppress('clearance', number) &
                          Tag.suppress('zone_connect', number))

    @classmethod
    def from_tag(cls, tag):
        assert tag.tag == 'pad'

        drill = tag['drill']
        if drill is not None:
            drill = Drill.from_tag(tag['drill'])

        rect_delta = tag['rect_delta']
        if rect_delta is not None:
            rect_delta = rect_delta.value()

        return cls(name=tag[0], type=tag[1], shape=tag[2],
                   at=tag['at'].value(), size=tag['size'].value(),
                   layers=tag['layers'].value(),
                   drill=drill,
                   rect_delta=rect_delta)

    def to_tag(self):
        if self.drill is None:
            drill = []
        else:
            drill = [self.drill.to_tag()]

        if self.rect_delta is None:
            rect_delta = []
        else:
            rect_delta = [Tag('rect_delta', *self.rect_delta)]

        return Tag('pad', self.name, self.type, self.shape,
                   Tag('at', *self.at),
                   Tag('size', *self.size),
                   Tag('layers', *self.layers),
                   *(drill + rect_delta))

    def __str__(self):
        return 'Pad: %s\n' % repr(self.to_tag())

    def __repr__(self):
        return repr(self.to_tag())


class Text(object):
    def __init__(self, prop, value, at, layer='F.SilkS',
                 hide=False, size=[1, 1], thickness=1):
        self.prop = prop
        self.value = value
        self.at = at
        self.layer = layer
        self.size = size
        self.thickness = thickness

    @staticmethod
    def parser():
        return Tag.parser('fp_text', name, text,
                          Tag.parser('at', number, number,
                                     # Bug in some package definitions?
                                     Suppress(Optional(number))) &
                          Tag.parser('layer', name) &
                          Tag.parser('effects',
                                     Tag.parser('font',
                                                Tag.parser('size', number, number) &
                                                Tag.parser('thickness', number))) &
                          # Don't currently need this attribute
                          Optional('hide'))

    @classmethod
    def from_tag(cls, tag):
        assert tag.tag == 'fp_text'
        return cls(prop=tag[0], value=tag[1],
                   at=tag['at'].value(),
                   layer=tag['layer'].value(),
                   size=tag['effects']['font']['size'].value(),
                   thickness=tag['effects']['font']['thickness'].value())

    def to_tag(self):
        return Tag('fp_text', self.prop, self.value,
                   Tag('at', *self.at),
                   Tag('layer', self.layer),
                   Tag('effects',
                       Tag('font',
                           Tag('size', *self.size),
                           Tag('thickness', self.thickness))))

    def __str__(self):
        return 'Text: %s\n' % repr(self.to_tag())

    def __repr__(self):
        return repr(self.to_tag())


class Line(object):
    def __init__(self, start, end, layer='F.SilkS', width=None):
        self.start = start
        self.end = end
        self.layer = layer
        self.width = width

    @staticmethod
    def parser():
        return Tag.parser('fp_line',
                          Tag.parser('start', number, number) &
                          Tag.parser('end', number, number) &
                          Tag.parser('layer', name) &
                          Optional(Tag.parser('width', number)))

    @classmethod
    def from_tag(cls, tag):
        assert tag.tag == 'fp_line'
        return cls(start=tag['start'].value(),
                   end=tag['end'].value(),
                   layer=tag['layer'].value(),
                   width=tag['width'].value())

    def to_tag(self):
        return Tag('fp_line',
                   Tag('start', *self.start),
                   Tag('end', *self.end),
                   Tag('layer', self.layer),
                   Tag('width', self.width))

    def __str__(self):
        return 'Line: %s\n' % repr(self.to_tag())

    def __repr__(self):
        return repr(self.to_tag())


class Circle(object):
    def __init__(self, center, end, layer='F.SilkS', width=None):
        self.center = center
        self.end = end
        self.layer = layer
        self.width = width

    @staticmethod
    def parser():
        return Tag.parser('fp_circle',
                          Tag.parser('center', number, number) &
                          Tag.parser('end', number, number) &
                          Tag.parser('layer', name) &
                          Tag.parser('width', number))

    @classmethod
    def from_tag(cls, tag):
        assert tag.tag == 'fp_circle'
        return cls(center=tag['center'].value(),
                   end=tag['end'].value(),
                   layer=tag['layer'].value(),
                   width=tag['width'].value())

    def to_tag(self):
        return Tag('fp_circle',
                   Tag('center', *self.center),
                   Tag('end', *self.end),
                   Tag('layer', self.layer),
                   Tag('width', self.width))

    def __str__(self):
        return 'Circle: %s\n' % repr(self.to_tag())

    def __repr__(self):
        return repr(self.to_tag())


class Arc(object):
    def __init__(self, start, end, angle, layer='F.SilkS', width=None):
        self.start = start
        self.end = end
        self.angle = angle
        self.layer = layer
        self.width = width

    @staticmethod
    def parser():
        return Tag.parser('fp_arc',
                          Tag.parser('start', number, number) &
                          Tag.parser('end', number, number) &
                          Tag.parser('angle', number) &
                          Tag.parser('layer', name) &
                          Tag.parser('width', number))

    @classmethod
    def from_tag(cls, tag):
        assert tag.tag == 'fp_arc'
        return cls(tag['start'].value(),
                   tag['end'].value(),
                   tag['angle'].value(),
                   tag['layer'].value(),
                   tag['width'].value())

    def to_tag(self):
        return Tag('fp_arc',
                   Tag('start', *self.start),
                   Tag('end', *self.end),
                   Tag('angle', self.angle),
                   Tag('layer', self.layer),
                   Tag('width', self.width))

    def __str__(self):
        return 'Arc: %s\n' % repr(self.to_tag())

    def __repr__(self):
        return repr(self.to_tag())


class Module(object):
    def __init__(self, name, descr=None, tags=None, layer='F.Cu',
                 pads=None, texts=None, lines=None, circles=None,
                 arcs=None, model=None):
        self.name = name
        self.descr = descr
        self.layer = layer
        self.tags = tags
        self.pads = pads or []
        self.texts = texts or []
        self.lines = lines or []
        self.circles = circles or []
        self.arcs = arcs or []
        self.model = model


    @staticmethod
    def parser():
        return Tag.parser('module', name,
                          Tag.parser('layer', name) &
                          Optional(Tag.parser('descr', text)) &
                          Optional(Tag.parser('tags', text)) &
                          ZeroOrMore(Text.parser()) &
                          ZeroOrMore(Line.parser()) &
                          ZeroOrMore(Circle.parser()) &
                          ZeroOrMore(Arc.parser()) &
                          ZeroOrMore(Pad.parser()) &
                          Optional(Model.parser()) &
                          Tag.suppress('attr', name) &
                          Tag.suppress('at', number, number) &
                          Tag.suppress('tedit', text) &
                          Tag.suppress('solder_mask_margin', number))

    def to_tag(self):
        children = []

        if self.descr is not None:
            children.append(Tag('descr', self.descr))

        if self.tags is not None:
            children.append(Tag('tags', self.tags))

        children += self.pads + self.texts + self.lines + \
                    self.circles + self.arcs

        if self.model is not None:
            children.append(self.model)

        return Tag('module', self.name,
                   Tag('layer', self.layer),
                   *children)

    @classmethod
    def from_tag(cls, tag):
        assert tag.tag == 'module'
        texts, lines, circles, arcs, pads = [], [], [], [], []

        descr = tag['descr']
        if descr is not None:
            descr = descr.value()

        tags = tag['tags']
        if tags is not None:
            tags = tags.value()

        for pad in tag['pad'] or []:
            pads.append(Pad.from_tag(pad))

        for text in tag['fp_text'] or []:
            texts.append(Text.from_tag(text))

        for line in tag['fp_line'] or []:
            lines.append(Line.from_tag(line))

        for circle in tag['fp_circle'] or []:
            circles.append(Circle.from_tag(circle))

        for arc in tag['fp_arc'] or []:
            arcs.append(Arc.from_tag(arc))

        model = tag['model']
        if model is not None:
            model = Model.from_tag(model)

        return cls(name=tag[0], descr=descr, tags=tags, layer=tag['layer'].value(),
                   texts=texts, lines=lines, circles=circles, arcs=arcs,
                   pads=pads, model=model)

    @staticmethod
    def parse(string):
        return Module.from_tag(Module.parser().parseString(string)[0])

    def __str__(self):
        string = 'Module: %s\nDescription: %s\nTags: %s\nLayer: %s\n' % \
                 (self.name, self.descr, self.tags, self.layer)

        for child in (self.pads + self.texts + self.lines +
                      self.circles + self.arcs):
            string += str(child)
        if self.model is not None:
            string += str(self.model)
        return string

    def __repr__(self):
        return repr(self.to_tag())


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


def debug_print(text):
    for i, line in enumerate(text.split('\n')):
        sys.stdout.buffer.write(("%4d: %s\n" % (i + 1, line)).encode('utf-8'))


def parse_module(path):
    module = open(path, 'r', encoding='utf-8').read()

    try:
        return Module.parse(module)
    except:
        debug_print(module)
        raise
