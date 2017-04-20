# Routines for generating and parsing KiCAD files

There are multiple python scripts that read and write kicad file
formats. Currently there is the problem that each project reimplements
basic parsing and serialization of these formats.

The aim of this project is to provide high quality and well tested
format support so that other projects can focus on the interesting
stuff.


## Usage
```python
from pykicad.pcb import *
from pykicad.module import *

vi, vo, gnd = Net(1, 'VI'), Net(2, 'VO'), Net(3, 'GND')

r1 = Module.from_library('Resistors_SMD', 'R_0805')
r2 = Module.from_library('Resistors_SMD', 'R_0805')

r1.pads[0].net = vi
r1.pads[1].net = vo
r2.pads[0].net = vo
r2.pads[1].net = gnd

pcb = Pcb()
pcb.modules += [r1, r2]
pcb.nets += [vi, vo, gnd]

with open('project.kicad_pcb', 'w+') as f:
    f.write(str(pcb))
```


## Supported file formats

* Modules (*.pretty, *.kicad_mod) in module.py
* Pcbnew (*.kicad_pcb) in pcb.py


# API docs
## modules.py
### Classes
* Module(name, descr, tags, layer, pads, texts, lines, circles, arcs, model)
* Pad(name, type, shape, drill, at, size, rect_delta, layers)
* Drill(size, offset)
* Net(code, name)
* Model(path, at, scale, rotate)
* Text(prop, value, at, layer, hide, size, thickness)
* Line(start, end, layer, width)
* Circle(center, end, layer, width)
* Arc(start, end, angle, layer, width)

### Functions
* find_library(library)
* find_module(library, module)
* list_libraries()
* list_modules(library)
* list_all_modules()

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
