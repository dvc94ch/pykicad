# Routines for generating and parsing KiCAD files

There are multiple python scripts that read and write kicad file
formats. Currently there is the problem that each project reimplements
basic parsing and serialization of these formats.

The aim of this project is to provide high quality and well tested
format support so that other projects can focus on the interesting
stuff.

## Status
Complete support for the kicad_pcb and kicad_mod formats.  The schemas of the
classes should provide good documentation on the kicad file format.  A summary
of all methods and fields can be found in the section API docs.

## Usage
```python
from numpy import array
from pykicad.pcb import *
from pykicad.module import *

# Define nets
vi, vo, gnd = Net('VI'), Net('VO'), Net('GND')

# Load footprints
r1 = Module.from_library('Resistors_SMD', 'R_0805')
r2 = Module.from_library('Resistors_SMD', 'R_0805')

# Connect pads
r1.pads[0].net = vi
r1.pads[1].net = vo
r2.pads[0].net = vo
r2.pads[1].net = gnd

# Place components
r1.at = [0, 0]
r2.at = [5, 0]

# Compute positions
start = array(r1.pads[1].at) + array(r1.at)
end = array(r2.pads[0].at) + array(r2.at)
pos = start + (end - start) / 2

# Create vias
v1 = Via(at=pos.tolist(), size=.8, drill=.6, net=vo.code)

# Create segments
s1 = Segment(start=start.tolist(), end=pos.tolist(), net=vo.code)
s2 = Segment(start=pos.tolist(), end=end.tolist(), net=vo.code)


layers = [
    Layer('F.Cu'),
    Layer('Inner1.Cu'),
    Layer('Inner2.Cu'),
    Layer('B.Cu'),
    Layer('Edge.Cuts', type='user')
]

for layer in ['Mask', 'Paste', 'SilkS', 'CrtYd', 'Fab']:
    for side in ['B', 'F']:
        layers.append(Layer('%s.%s' % (side, layer), type='user'))

nc1 = NetClass('default', trace_width=1, nets=['VI', 'VO', 'GND'])

# Create PCB
pcb = Pcb()
pcb.title = 'A title'
pcb.comment1 = 'Comment 1'
pcb.page_type = [20, 20]
pcb.num_nets = 5
pcb.setup = Setup(grid_origin=[10, 10])
pcb.layers = layers
pcb.modules += [r1, r2]
pcb.net_classes += [nc1]
pcb.nets += [vi, vo, gnd]
pcb.segments += [s1, s2]
pcb.vias += [v1]


pcb.to_file('project')
```


## Supported file formats

* Modules (*.pretty, *.kicad_mod) in module.py
* Pcbnew (*.kicad_pcb) in pcb.py


# API docs
## modules.py
### Classes
* Module(name, version, locked, placed, layer, tedit, tstamp, at, descr, tags,
         path, attr, autoplace_cost90, autoplace_cost180, solder_mask_margin,
         solder_paste_margin, solder_paste_ratio, clearance, zone_connect,
         thermal_width, thermal_gap, texts, lines, circles, arcs, curves,
         polygons, pads, models)
  * pads_by_name(name)
  * set_reference(name)
  * set_value(value)
  * geometry()
  * elements_by_layer(layer)
  * courtyard()
  * place(x, y)
  * rotate(angle)
  * connect(pad, net)
  * flip()
  * from_file(cls, path)
  * from_library(cls, lib, name)
* Pad(name, type, shape, size, at, rect_delta, roundrect_rratio, drill, layers,
      net, die_length, solder_mask_margin, solder_paste_margin, solder_paste_margin_ratio,
      clearance, zone_connect)
  * rotate(angle)
  * flip()
* Drill(size, offset)
* Net(code, name)
* Model(path, at, scale, rotate)
* Text(type, text, at, layer, size, thickness, bold, italic, justify, hide, tstamp)
  * rotate(angle)
  * flip()
* Line(start, end, layer, width, tstamp, status)
  * flip()
* Circle(center, end, layer, width, tstamp, status)
  * flip()
* Arc(start, end, angle, layer, width, tstamp, status)
  * flip()
* Polygon(pts, layer, width, tstamp, status)
  * flip()
* Curve(start, bezier1, bezier2, end, layer, width, tstamp, status)
  * flip()

## pcb.py
### Classes
* Pcb(version, host, board_thickness, num_nets, num_no_connects, title, date, rev,
      company, comment1, comment2, comment3, comment4, page_type, portrait,
      setup, layers, nets, net_classes, modules, segments, vias, texts, lines,
      arcs, circles, polygons, curves, zones, targets, dimensions)
  * geometry()
  * elements_by_layer(layer)
  * outline()
  * module_by_reference(name)
  * net_by_code(code)
  * to_file(path)
  * from_file(cls, path)
* Segment(start, end, net, width, layer, tstamp, status)
* Text(text, at, layer, size, thickness, bold, italic, justify, hide, tstamp)
* Line(start, end, width, layer, tstamp, status)
* Arc(start, end, angle, layer, width)
* Circle(center, end, layer, width, tstamp, status)
* Polygon(pts, layer, width, tstamp, status)
* Curve(start, bezier1, bezier2, end, layer, width, tstamp, status)
* Via(micro, blind, at, size, drill, layers, net, tstamp, status)
* Layer(code, name, type, hide)
* NetClass(name, description, clearance, trace_width, via_dia, via_drill,
           uvia_dia, uvia_drill, diff_pair_width, diff_pair_gap, nets)
* Zone(net, net_name, layer, tstamp, hatch_type, hatch_size, priority,
       connect_pads, clearance, min_thickness, fill, fill_mode, arc_segments,
       thermal_gap, thermal_bridge_width, smoothing, radius, keepout_tracks,
       keepout_vias, keepout_copperpour, polygon, filled_polygon, fill_segments)
* Target(shape, at, size, width, layer, tstamp)
* Dimension(value, width, layer, text, feature1, feature2, crossbar, arrow1a,
            arrow1b, arrow2a, arrow2b, tstamp)
* Setup(user_trace_width, trace_clearance, zone_clearance, zone_45_only,
        trace_min, segment_width, edge_width, via_size, uvia_size,
        uvia_drill, uvias_allowed, blind_buried_vias_allowed, uvia_min_size,
        uvai_min_drill, pcb_text_width, pcb_text_size, mod_edge_width,
        mod_text_size, mod_text_width, pad_size, pad_drill, pad_to_mask_clearance,
        solder_mask_min_width, pad_to_paste_clearance, solder_to_paste_clearance_ratio,
        grid_origin, visible_elements, pcbplotparams)

### Functions
* find_library(library)
* find_module(library, module)
* list_libraries()
* list_modules(library)
* list_all_modules()
* filter_by_regex()
* flip_layer()

### Global variables
* MODULE_SEARCH_PATH

# Project using pykicad
* [pycircuit] (https://github.com/dvc94ch/pycircuit)

# License
ISC License

Copyright (c) 2017, David Craven

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
