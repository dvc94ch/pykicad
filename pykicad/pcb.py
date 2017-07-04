from pykicad.sexpr import *
from pykicad.module import Module, Net


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

class Line(AST):
    tag = 'gr_line'
    schema = {
        '0': {
            '_tag': 'start',
            '_parser': number + number
        },
        '1': {
            '_tag': 'end',
            '_parser': number + number,
        },
        'width': number,
        'layer': text,
        'tstamp': hex,
    }

    def __init__(self, start, end, width=None, layer='F.Cu',
                 tstamp=None):
        super(Line, self).__init__(start=start, end=end, width=width,
                                   layer=layer, tstamp=tstamp)


class Via(AST):
    tag = 'via'
    schema = {
        'micro': flag('micro'),
        'blind': flag('blind'),
        'at': number + number,
        'size': number,
        'drill': number,
        'layers': Group(OneOrMore(text)).setParseAction(lambda x: [list(x[0])]),
        'net': integer,
        'tstamp': hex,
        'status': hex
    }

    def __init__(self, at, size, drill, net, micro=False, blind=False, layers=None,
                 tstamp=None, status=None):

        layers = self.init_list(layers, ['F.Cu', 'B.Cu'])

        super(Via, self).__init__(micro=micro, blind=blind, at=at, size=size,
                                  drill=drill, layers=layers, net=net,
                                  tstamp=tstamp, status=status)


class Layer(AST):
    tag = ''
    schema = {
        '0': {
            '_parser': integer,
            '_attr': 'code'
        },
        '1': {
            '_parser': text,
            '_attr': 'name'
        },
        '2': {
            '_parser': Literal('signal') | 'power' | 'mixed' | 'jumper' | 'user',
            '_attr': 'type'
        },
        'hide': flag('hide')
    }
    cu_counter = 0
    user_counter = 32

    def __init__(self, name, code=None, type='signal', hide=None):
        if code is None:
            if type == 'user':
                code = Layer.user_counter
                Layer.user_counter += 1
            else:
                code = Layer.cu_counter
                Layer.cu_counter += 1

        super(Layer, self).__init__(code=code, name=name, type=type, hide=hide)


class NetClass(AST):
    tag = 'net_class'
    schema = {
        '0': {
            '_parser': text,
            '_attr': 'name'
        },
        '1': {
            '_parser': text,
            '_attr': 'description'
        },
        'clearance': number,
        'trace_width': number,
        'via_dia': number,
        'via_drill': number,
        'uvia_dia': number,
        'uvia_drill': number,
        'diff_pair_width': number,
        'diff_pair_gap': number,
        'nets': {
            '_tag': 'add_net',
            '_attr': 'nets',
            '_parser': text,
            '_multiple': True,
            '_printer': lambda x: '(add_net %s)' % x
        }
    }

    def __init__(self, name, description='', clearance=None, trace_width=None,
                 via_dia=None, via_drill=None, uvia_dia=None, uvia_drill=None,
                 diff_pair_width=None, diff_pair_gap=None, nets=None):

        nets = self.init_list(nets, [])

        super(NetClass, self).__init__(name=name, description=description,
                                       clearance=clearance, trace_width=trace_width,
                                       via_dia=via_dia, via_drill=via_drill,
                                       uvia_dia=uvia_dia, uvia_drill=uvia_drill,
                                       diff_pair_width=diff_pair_width,
                                       diff_pair_gap=diff_pair_gap,
                                       nets=nets)


class Setup(AST):
    tag = 'setup'
    schema = {
        'last_trace_width': number,
        'user_trace_width': number,
        'trace_clearance': number,
        'zone_clearance': number,
        'zone_45_only': yes_no,
        'trace_min': number,
        'segment_width': number,
        'edge_width': number,
        'via_size': number,
        'via_drill': number,
        'via_min_size': number,
        'via_min_drill': number,
        'user_via': number + number,
        'uvia_size': number,
        'uvia_drill': number,
        'uvias_allowed': yes_no,
        'blind_buried_vias_allowed': yes_no,
        'uvia_min_size': number,
        'uvia_min_drill': number,
        'pcb_text_width': number,
        'pcb_text_size': number + number,
        'mod_edge_width': number,
        'mod_text_size': number + number,
        'mod_text_width': number,
        'pad_size': number + number,
        'pad_drill': number,
        'pad_to_mask_clearance': number,
        'solder_mask_min_width': number,
        'pad_to_paste_clearance': number,
        'pad_to_paste_clearance_ratio': number,
        'grid_origin': number + number,
        'aux_axis_origin': number + number,
        'visible_elements': hex,
        'pcbplotparams': {
            'layerselection': text,
            'usegerberextensions': boolean,
            'excludeedgelayer': boolean,
            'linewidth': number,
            'plotframeref': boolean,
            'viasonmask': boolean,
            'mode': integer,
            'useauxorigin': boolean,
            'hpglpennumber': integer,
            'hpglpenspeed': integer,
            'hpglpendiameter': integer,
            'psnegative': boolean,
            'psa4output': boolean,
            'plotreference': boolean,
            'plotvalue': boolean,
            'plotinvisibletext': boolean,
            'padsonsilk': boolean,
            'subtractmaskfromsilk': boolean,
            'outputformat': integer,
            'mirror': boolean,
            'drillshape': integer,
            'scaleselection': integer,
            'outputdirectory': text
        },
    }

    def __init__(self, user_trace_width=None, trace_clearance=None,
                 zone_clearance=None, zone_45_only=None, trace_min=None,
                 segment_width=None, edge_width=None, via_size=None,
                 via_min_size=None, via_min_drill=None, user_via=None,
                 uvia_size=None, uvia_drill=None, uvias_allowed=None,
                 blind_buried_vias_allowed=None, uvia_min_size=None,
                 uvia_min_drill=None, pcb_text_width=None, pcb_text_size=None,
                 mod_edge_width=None, mod_text_size=None, mod_text_width=None,
                 pad_size=None, pad_drill=None, pad_to_mask_clearance=None,
                 solder_mask_min_width=None, pad_to_paste_clearance=None,
                 pad_to_paste_clearance_ratio=None, grid_origin=None,
                 visible_elements=None, pcbplotparams=None):
        super(Setup, self).__init__(user_trace_width=user_trace_width,
                                    trace_clearance=trace_clearance,
                                    zone_clearance=zone_clearance,
                                    zone_45_only=zone_45_only,
                                    trace_min=trace_min,
                                    segment_width=segment_width,
                                    edge_width=edge_width,
                                    via_size=via_size,
                                    via_min_size=via_min_size,
                                    via_min_drill=via_min_drill,
                                    user_via=user_via,
                                    uvia_size=uvia_size,
                                    uvia_drill=uvia_drill,
                                    uvias_allowed=uvias_allowed,
                                    blind_buried_vias_allowed=blind_buried_vias_allowed,
                                    uvia_min_size=uvia_min_size,
                                    uvia_min_drill=uvia_min_drill,
                                    pcb_text_width=pcb_text_width,
                                    pcb_text_size=pcb_text_size,
                                    mod_edge_width=mod_edge_width,
                                    mod_text_size=mod_text_size,
                                    mod_text_width=mod_text_width,
                                    pad_size=pad_size,
                                    pad_drill=pad_drill,
                                    pad_to_mask_clearance=pad_to_mask_clearance,
                                    solder_mask_min_width=solder_mask_min_width,
                                    pad_to_paste_clearance=pad_to_paste_clearance,
                                    pad_to_paste_clearance_ratio=pad_to_paste_clearance_ratio,
                                    grid_origin=grid_origin,
                                    visible_elements=visible_elements,
                                    pcbplotparams=pcbplotparams)


def comment(number):
    str_num = str(number)
    return {
        '_tag': 'comment',
        '_attr': 'comment' + str_num,
        '_parser': Suppress(str_num) + text,
        '_printer': (lambda x: '(comment %s %s)' %
                     (str_num, tree_to_string(x)))
    }


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
        'general': {
            'thickness': {
                '_parser': number,
                '_attr': 'board_thickness'
            },
            'area': {
                '_parser': number + number + number + number,
                '_attr': 'board_area'
            },
            'nets': {
                '_parser': integer,
                '_attr': 'num_nets'
            },
            'tracks': {
                '_parser': integer,
                '_attr': 'num_tracks'
            },
            'zones': {
                '_parser': integer,
                '_attr': 'num_zones'
            },
            'modules': {
                '_parser': integer,
                '_attr': 'num_modules'
            },
            'no_connects': {
                '_parser': integer,
                '_attr': 'num_no_connects'
            },
            'drawings': {
                '_parser': integer,
                '_attr': 'num_drawings'
            },
            'links': {
                '_parser': integer,
                '_attr': 'num_links'
            },
        },
        'title_block': {
            'title': text,
            'date': text,
            'rev': text,
            'company': text,
            'comment1': comment(1),
            'comment2': comment(2),
            'comment3': comment(3),
            'comment4': comment(4)
        },
        'page': {
            '0': {
                '_parser': Literal('A4') | 'A3' | 'A2' | 'A1' | 'A0' | \
                    'A' | 'B' | 'C' | 'D' | 'E' | \
                    'USLedger' | 'USLegal' | 'USLetter' | \
                    'GERBER' | (Suppress('User') + number + number),
                '_attr': 'page_type',
                '_printer': (lambda x: 'User %d %d' % (x[0], x[1])
                             if isinstance(x, list) else x)
            },
            'portrait': flag('portrait')
        },
        'setup': Setup,
        'layers': {
            'layers': {
                '_parser': Layer,
                '_multiple': True
            }
        },
        'net_classes': {
            '_parser': NetClass,
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
        },
        'lines': {
            '_parser': Line,
            '_multiple': True
        }
    }

    def __init__(self, version=1, host=['pykicad', 'x.x.x'],
                 board_thickness=None, board_area=None,
                 num_nets=None, num_no_connects=None, num_tracks=None,
                 num_zones=None, num_modules=None, num_drawings=None,
                 num_links=None, title=None, date=None, rev=None, company=None,
                 comment1=None, comment2=None, comment3=None, comment4=None,
                 page_type=None, portrait=None, setup=None,
                 layers=None, nets=None, net_classes=None, modules=None,
                 segments=None, vias=None, lines=None):

        layers = self.init_list(layers, [])
        nets = self.init_list(nets, [])
        net_classes = self.init_list(net_classes, [])
        modules = self.init_list(modules, [])
        segments = self.init_list(segments, [])
        vias = self.init_list(vias, [])
        lines = self.init_list(lines, [])

        super(Pcb, self).__init__(version=version, host=host,
                                  board_thickness=board_thickness,
                                  num_nets=num_nets, num_no_connects=num_no_connects,
                                  title=title, date=date, rev=rev, company=company,
                                  comment1=comment1, comment2=comment2,
                                  comment3=comment3, comment4=comment4,
                                  page_type=page_type, portrait=portrait,
                                  setup=setup, layers=layers, nets=nets,
                                  net_classes=net_classes, modules=modules,
                                  segments=segments, vias=vias, lines=lines)

    def module_by_reference(self, name):
        '''Returns a module called name.'''

        for module in self.modules:
            if module.name == name:
                return module

    def net_by_code(self, code):
        '''Returns a net with code.'''

        for net in self.nets:
            if net.code == code:
                return net

    @classmethod
    def from_file(cls, path):
        return Pcb.parse(open(path, encoding='utf-8').read())
