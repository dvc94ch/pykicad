from pykicad.sexpr import *
from pykicad.module import Module, Net, Drill


class Segment(AST):
    tag = 'segment'
    schema = {
        'start': number + number,
        'end': number + number,
        'width': number,
        'layer': text,
        'net': integer,
        'tstamp': hex,
        'status': hex
    }

    def __init__(self, start, end, net, width=None, layer='F.Cu',
                 tstamp=None, status=None):
        super(Segment, self).__init__(start=start, end=end, width=width,
                                      layer=layer, net=net, tstamp=tstamp,
                                      status=status)


class Via(AST):
    tag = 'via'
    schema = {
        'micro': flag('micro'),
        'blind': flag('blind'),
        'at': number + number,
        'size': number,
        'drill': Drill,
        'layers': Group(OneOrMore(text)).setParseAction(lambda x: [list(x[0])]),
        'net': integer,
        'tstamp': hex,
        'status': hex
    }

    def __init__(self, at, size, drill, net, micro=False, blind=False, layers=['F.Cu', 'B.Cu'],
                 tstamp=None, status=None):
        super(Via, self).__init__(micro=micro, blind=blind, at=at, size=size,
                                  drill=drill, layers=layers, net=net,
                                  tstamp=tstamp, status=status)


class Pcb(AST):
    tag = 'kicad_pcb'
    schema = {
        '0': {
            '_tag': 'version',
            '_parser': integer
        },
        '1': {
            '_tag': 'host',
            '_parser': text + text
        },
        '2': {
            '_attr': 'nets',
            '_parser': Net,
            '_multiple': True
        },
        'modules': {
            '_parser': Module,
            '_multiple': True
        },
        'segments': {
            '_parser': Segment,
            '_multiple': True
        },
        'vias': {
            '_parser': Via,
            '_multiple': True
        }
    }

    def __init__(self, version=1, host=['pykicad', 'x.x.x'], nets=[], modules=[],
                 segments=[], vias=[]):
        super(Pcb, self).__init__(version=version, host=host, nets=nets,
                                  modules=modules, segments=segments, vias=vias)
