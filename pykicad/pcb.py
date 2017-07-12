from pykicad.sexpr import *
from pykicad.module import Module, Net, xy_schema


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


class Text(AST):
    tag = 'gr_text'
    schema = {
        '0': {
            '_attr': 'text',
            '_parser': text
        },
        '1': {
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
        'hide': flag('hide'),
        'tstamp': hex
    }

    def __init__(self, text, at, layer='F.SilkS', size=None, thickness=None,
                 bold=False, italic=False, justify=None, hide=False, tstamp=None):

        super(Text, self).__init__(text=text, at=at, layer=layer, size=size,
                                   thickness=thickness, bold=bold, italic=italic,
                                   justify=justify, hide=hide, tstamp=tstamp)


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
        'layer': text,
        'width': number,
        'tstamp': hex,
        'status': hex
    }

    def __init__(self, start, end, layer='Edge.Cuts', width=None,
                 tstamp=None, status=None):
        super(Line, self).__init__(start=start, end=end, layer=layer, width=width,
                                   tstamp=tstamp, status=status)


class Arc(AST):
    tag = 'gr_arc'
    schema = {
        '0': {
            '_tag': 'start',
            '_parser': number + number
        },
        '1': {
            '_tag': 'end',
            '_parser': number + number
        },
        'angle': number,
        'layer': text,
        'width': number,
        'tstamp': hex,
        'status': hex
    }

    def __init__(self, start, end, angle, layer='Edge.Cuts', width=None,
                 tstamp=None, status=None):
        super(Arc, self).__init__(start=start, end=end, angle=angle, layer=layer,
                                  width=width, tstamp=tstamp, status=status)


class Circle(AST):
    tag = 'gr_circle'
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
        'width': number,
        'tstamp': hex,
        'status': hex
    }

    def __init__(self, center, end, layer='Edge.Cuts', width=None,
                 tstamp=None, status=None):
        super(Circle, self).__init__(center=center, end=end, layer=layer,
                                     width=width, tstamp=tstamp, status=status)


class Polygon(AST):
    tag = 'gr_poly'
    schema = {
        '0': {
            'pts': xy_schema('pts'),
        },
        'layer': text,
        'width': number,
        'tstamp': hex,
        'status': hex
    }

    def __init__(self, pts, layer='Edge.Cuts', width=None, tstamp=None, status=None):
        super(Polygon, self).__init__(pts=pts, layer=layer, width=width,
                                      tstamp=tstamp, status=status)


class Curve(AST):
    tag = 'gr_curve'
    schema = {
        '0': {
            'pts': {
                '0': {
                    'xy': {
                        '_attr': 'start',
                        '_parser': tuple_parser(2)
                    }
                },
                '1': {
                    'xy': {
                        '_attr': 'bezier1',
                        '_parser': tuple_parser(2)
                    }
                },
                '2': {
                    'xy': {
                        '_attr': 'bezier2',
                        '_parser': tuple_parser(2)
                    }
                },
                '3': {
                    'xy': {
                        '_attr': 'end',
                        '_parser': tuple_parser(2)
                    }
                }
            },
            'layer': text,
            'width': number,
            'tstamp': hex,
            'status': hex
        }
    }

    def __init__(self, start, bezier1, bezier2, end, layer='Edge.Cuts',
                 width=None, tstamp=None, status=None):
        super(Curve, self).__init__(start=start, bezier1=bezier1,
                                    bezier2=bezier2, end=end, layer=layer,
                                    width=width, tstamp=tstamp, status=status)


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


class Zone(AST):
    tag = 'zone'
    schema = {
        'net': integer,
        'net_name': text,
        'layer': text,
        'tstamp': hex,
        'hatch': {
            '0': {
                '_attr': 'hatch_type',
                '_parser': Literal('none') | 'edge' | 'full'
            },
            '1': {
                '_attr': 'hatch_size',
                '_parser': number
            }
        },
        'priority': number,
        'connect_pads': {
            '0': {
                '_attr': 'connect_pads',
                '_tag': False,
                '_parser': Literal('yes') | 'no' | 'thru_hole_only'
            },
            'clearance': number
        },
        'min_thickness': number,
        'fill': {
            '0': extend_schema(yes_no('fill')['0'], _tag=False, _optional=True),
            'mode': {
                '_attr': 'fill_mode',
                '_parser': Literal('segment') | 'polygon'
            },
            'arc_segments': integer,
            'thermal_gap': number,
            'thermal_bridge_width': number,
            'smoothing': Literal('none') | 'chamfer' | 'fillet',
            'radius': number
        },
        'keepout': {
            'tracks': allowed('keepout_tracks'),
            'vias': allowed('keepout_vias'),
            'copperpour': allowed('keepout_copperpour')
        },
        'polygon': {
            'pts': xy_schema('polygon')
        },
        'filled_polygon': {
            'pts': xy_schema('filled_polygon')
        },
        'fill_segments': {
            'pts': xy_schema('fill_segments')
        }
    }

    def __init__(self, net=None, net_name=None, layer=None, tstamp=None,
                 hatch_type=None, hatch_size=None, priority=None, connect_pads=None,
                 clearance=None, min_thickness=None, fill=True, fill_mode=None,
                 arc_segments=None, thermal_gap=None, thermal_bridge_width=None,
                 smoothing=None, radius=None, keepout_tracks=None, keepout_vias=None,
                 keepout_copperpour=None, polygon=None, filled_polygon=None,
                 fill_segments=None):

        super(Zone, self).__init__(net=net, net_name=net_name, layer=layer,
                                   tstamp=tstamp, hatch_type=hatch_type,
                                   hatch_size=hatch_size, priority=priority,
                                   connect_pads=connect_pads, clearance=clearance,
                                   min_thickness=min_thickness, fill=fill,
                                   fill_mode=fill_mode, arc_segments=arc_segments,
                                   thermal_gap=thermal_gap,
                                   thermal_bridge_width=thermal_bridge_width,
                                   smoothing=smoothing, radius=radius,
                                   keepout_tracks=keepout_tracks,
                                   keepout_vias=keepout_vias,
                                   keepout_copperpour=keepout_copperpour,
                                   polygon=polygon, filled_polygon=filled_polygon,
                                   fill_segments=fill_segments)


class Target(AST):
    tag = 'target'
    schema = {
        'shape': {
            '_tag': False,
            '_attr': 'shape',
            '_parser': Literal('x') | 'plus',
            '_printer': lambda x: x
        },
        'at': number + number,
        'size': number,
        'width': number,
        'layer': text,
        'tstamp': hex
    }

    def __init__(self, shape, at, size=None, width=None,
                 layer='Edge.Cuts', tstamp=None):
        super(Target, self).__init__(shape=shape, at=at, size=size, width=width,
                                     layer=layer, tstamp=tstamp)


class Dimension(AST):
    tag = 'dimension'
    schema = {
        '0': {
            '_attr': 'value',
            '_parser': number
        },
        '1': {
            '_tag': 'width',
            '_parser': number
        },
        'layer': text,
        'text': Text,
        'feature1': {
            'pts': xy_schema('feature1')
        },
        'feature2': {
            'pts': xy_schema('feature2')
        },
        'crossbar': {
            'pts': xy_schema('crossbar')
        },
        'arrow1a': {
            'pts': xy_schema('arrow1a')
        },
        'arrow1b': {
            'pts': xy_schema('arrow1b')
        },
        'arrow2a': {
            'pts': xy_schema('arrow2a')
        },
        'arrow2b': {
            'pts': xy_schema('arrow2b')
        },
        'tstamp': hex
    }

    def __init__(self, value, width, layer='F.SilkS', text=None, feature1=None,
                 feature2=None, crossbar=None, arrow1a=None, arrow1b=None,
                 arrow2a=None, arrow2b=None, tstamp=None):
        super(Dimension, self).__init__(value=value, width=width, layer=layer,
                                        text=text, feature1=feature1,
                                        feature2=feature2, crossbar=crossbar,
                                        arrow1a=arrow1a, arrow1b=arrow1b,
                                        arrow2a=arrow2a, arrow2b=arrow2b,
                                        tstamp=tstamp)


class Setup(AST):
    tag = 'setup'
    schema = {
        'last_trace_width': number,
        'user_trace_width': number,
        'trace_clearance': number,
        'zone_clearance': number,
        'zone_45_only': yes_no('zone_45_only'),
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
        'uvias_allowed': yes_no('uvias_allowed'),
        'blind_buried_vias_allowed': yes_no('blind_buried_vias_allowed'),
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
            'usegerberextensions': boolean('usegerberextensions'),
            'excludeedgelayer': boolean('excludeedgelayer'),
            'linewidth': number,
            'plotframeref': boolean('plotframeref'),
            'viasonmask': boolean('viasonmask'),
            'mode': integer,
            'useauxorigin': boolean('useauxorigin'),
            'hpglpennumber': integer,
            'hpglpenspeed': integer,
            'hpglpendiameter': integer,
            'psnegative': boolean('psnegative'),
            'psa4output': boolean('psa4output'),
            'plotreference': boolean('plotreference'),
            'plotvalue': boolean('plotvalue'),
            'plotinvisibletext': boolean('plotinvisibletext'),
            'padsonsilk': boolean('padsonsilk'),
            'subtractmaskfromsilk': boolean('subtractmaskfromsilk'),
            'outputformat': integer,
            'mirror': boolean('mirror'),
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
            '_optional': True
        },
        '3': {
            'page': {
                '0': {
                    '_parser': Literal('A4') | 'A3' | 'A2' | 'A1' | 'A0' | \
                    'A' | 'B' | 'C' | 'D' | 'E' | \
                    'USLedger' | 'USLegal' | 'USLetter' | \
                    'GERBER' | (Suppress('User') + number + number),
                    '_attr': 'page_type',
                    '_printer': (lambda x: 'User %f %f' % (x[0], x[1])
                                 if isinstance(x, list) else x)
                },
                'portrait': flag('portrait')
            },
            '_optional': True
        },
        '4': {
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
            '_optional': True
        },
        '5': {
            'layers': {
                'layers': {
                    '_parser': Layer,
                    '_multiple': True
                },
                '_optional': True
            },
        },
        '6': {
            'setup': Setup,
            '_optional': True
        },
        '7': {
            '_attr': 'nets',
            '_parser': Net,
            '_multiple': True,
            '_optional': True
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
        'texts': {
            '_parser': Text,
            '_multiple': True
        },
        'lines': {
            '_parser': Line,
            '_multiple': True
        },
        'arcs': {
            '_parser': Arc,
            '_multiple': True
        },
        'circles': {
            '_parser': Circle,
            '_multiple': True
        },
        'polygons': {
            '_parser': Polygon,
            '_multiple': True
        },
        'curves': {
            '_parser': Curve,
            '_multiple': True
        },
        'zones': {
            '_parser': Zone,
            '_multiple': True
        },
        'targets': {
            '_parser': Target,
            '_multiple': True
        },
        'dimensions': {
            '_parser': Dimension,
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
                 segments=None, vias=None, texts=None, lines=None, arcs=None,
                 circles=None, polygons=None, curves=None, zones=None,
                 targets=None, dimensions=None):

        layers = self.init_list(layers, [])
        nets = self.init_list(nets, [])
        net_classes = self.init_list(net_classes, [])
        modules = self.init_list(modules, [])
        segments = self.init_list(segments, [])
        vias = self.init_list(vias, [])
        texts = self.init_list(texts, [])
        lines = self.init_list(lines, [])
        arcs = self.init_list(arcs, [])
        circles = self.init_list(circles, [])
        polygons = self.init_list(polygons, [])
        curves = self.init_list(curves, [])
        zones = self.init_list(zones, [])
        targets = self.init_list(targets, [])
        dimensions = self.init_list(dimensions, [])

        super(Pcb, self).__init__(version=version, host=host,
                                  board_thickness=board_thickness,
                                  num_nets=num_nets, num_no_connects=num_no_connects,
                                  title=title, date=date, rev=rev, company=company,
                                  comment1=comment1, comment2=comment2,
                                  comment3=comment3, comment4=comment4,
                                  page_type=page_type, portrait=portrait,
                                  setup=setup, layers=layers, nets=nets,
                                  net_classes=net_classes, modules=modules,
                                  segments=segments, vias=vias, texts=texts,
                                  lines=lines, arcs=arcs, circles=circles,
                                  polygons=polygons, curves=curves, zones=zones,
                                  targets=targets, dimensions=dimensions)

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

    def outline(self):
        '''Returns the outline of a pcb.'''

        return list(self.elements_by_layer('Edge.Cuts'))

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

    def to_file(self, path):
        if not path.endswith('.kicad_pcb'):
            path += '.kicad_pcb'
        with open(path, 'w+', encoding='utf-8') as f:
            f.write(self.to_string())

    @classmethod
    def from_file(cls, path):
        return Pcb.parse(open(path, encoding='utf-8').read())
