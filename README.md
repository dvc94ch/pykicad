# Routines for generating and parsing KiCAD files

There are multiple python scripts that read and write kicad file
formats. Currently there is the problem that each project reimplements
basic parsing and serialization of these formats.

The aim of this project is to provide high quality and well tested
format support so that other projects can focus on the interesting
stuff.


## Supported file formats

* Modules (*.pretty, *.kicad_mod) in module.py

## Formats that are on the TODO list

* Netlists (*.net)
* Pcbnew (*.kicad_pcb)
* Schematic symbols (*.lib)

# API docs
## modules.py
### Classes
Module(name, descr, tags, layer, pads, texts, lines, circles, arcs, model)
Pad(name, type, shape, drill, at, size, rect_delta, layers)
Drill(size, offset)
Model(path, at, scale, rotate)
Text(prop, value, at, layer, hide, size, thickness)
Line(start, end, layer, width)
Circle(center, end, layer, width)
Arc(start, end, angle, layer, width)

### Functions
find_library(library)
find_module(library, module)
list_libraries()
list_modules(library)
list_all_modules()
parse_module(path)

### Global variables
MODULE_SEARCH_PATH

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
