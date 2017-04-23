from pykicad.module import *

class Polygon(object):
    def scale(self, xfactor, yfactor):
        for i, (x, y) in enumerate(self.vertices):
            self.vertices[i] = (x * xfactor, y * yfactor)

    def to_lines(self, layer='F.SilkS'):
        lines = []
        for i, (xs, ys) in enumerate(self.vertices):
            xe, ye = self.vertices[(i + 1) % len(self.vertices)]
            line = Line(start=[xs, ys], end=[xe, ye], layer=layer)
            lines.append(line)
        return lines


class Rectangle(Polygon):
    def __init__(self, size):
        self.size = size
        self.vertices = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        self.scale(size[0] / 2, size[1] / 2)


def module_boundary(module):
    bl, tr = [0, 0], [0, 0]
    for line in module.lines:
        bl[0] = min(bl[0], line.start[0], line.end[0])
        bl[1] = min(bl[1], line.start[1], line.end[1])
        tr[0] = max(tr[0], line.start[0], line.end[0])
        tr[1] = max(tr[1], line.start[1], line.end[1])
    size = [tr[0] - bl[0], tr[1] - bl[1]]
    return Rectangle(size)


def draw_boundary(module):
    module.lines += module_boundary(module).to_lines()
    return module
