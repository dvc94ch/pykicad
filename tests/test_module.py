import unittest
from pytest import *
from pykicad.module import *


class DrillTests(unittest.TestCase):
    def test_drill(self):
        drill = Drill.parse('(drill 0.8)')
        assert drill.size == 0.8
        assert Drill.parse(drill.to_string()) == drill

    def test_drill_oval(self):
        drill = Drill.parse('(drill oval 0.6 0.8)')
        assert drill.size == [0.6, 0.8]
        assert Drill.parse(drill.to_string()) == drill

    def test_drill_offset(self):
        drill = Drill.parse('(drill 0.8 (offset 0.1 0.2))')
        assert drill.size == 0.8 and drill.offset == [0.1, 0.2]
        assert Drill.parse(drill.to_string()) == drill


class PadTests(unittest.TestCase):
    def test_pad(self):
        pad = Pad.parse(
            '(pad 1 smd rect (at 0.1 0.1) (size 0.2 0.2) (layers F.Cu))')
        assert pad.name == '1'
        assert pad.type == 'smd'
        assert pad.shape == 'rect'
        assert pad.at == [0.1, 0.1]
        assert pad.size == [0.2, 0.2]
        assert pad.layers == ['F.Cu']
        assert Pad.parse(pad.to_string()) == pad

    def test_pad_with_drill(self):
        pad = Pad.parse('(pad 1 smd rect (at 0.1 0.1) (size 0.2 0.2) '
                        '(layers F.Cu) (drill 0.8))')
        assert pad.drill.size == 0.8
        assert Pad.parse(pad.to_string()) == pad

    def test_pad_with_multiple_layers(self):
        pad = Pad.parse('(pad 1 smd rect (at 0.1 0.1) (size 0.2 0.2) '
                        '(layers F.Cu B.Cu))')
        assert pad.layers == ['F.Cu', 'B.Cu']
        assert Pad.parse(pad.to_string()) == pad


class TextTests(unittest.TestCase):
    def test_text(self):
        text = Text.parse('(fp_text user text (at 0.0 0.0) (layer F.SilkS))')
        assert text.type == 'user'
        assert text.text == 'text'
        assert text.at == [0.0, 0.0]
        assert text.layer == 'F.SilkS'
        assert Text.parse(text.to_string()) == text

    def test_text_with_rotation(self):
        text = Text.parse(
            '(fp_text user text (at 0.0 0.0 0.0) (layer F.SilkS))')
        assert text.at == [0.0, 0.0, 0.0]
        assert text.hide == False
        assert Text.parse(text.to_string()) == text

    def test_text_with_hide(self):
        text = Text.parse(
            '(fp_text user text (at 0.0 0.0) (layer F.SilkS) hide)')
        assert text.hide == True
        assert Text.parse(text.to_string()) == text

    def test_text_with_thickness(self):
        text = Text.parse('(fp_text user text (at 0.0 0.0) (layer F.SilkS) '
                          '(effects (font (size 0.1 0.1) (thickness 0.2))))')
        assert text.size == [0.1, 0.1]
        assert text.thickness == 0.2
        assert Text.parse(text.to_string()) == text

    def test_text_with_justify(self):
        text = Text.parse('(fp_text user text (at 0.0 0.0) (layer layer) '
                          '(effects (justify mirror)))')
        assert text.justify == 'mirror'
        assert Text.parse(text.to_string()) == text


class LineTests(unittest.TestCase):
    def test_line(self):
        line = Line.parse('(fp_line (start 0 0) (end 1 1) (layer layer))')
        assert line.start == [0.0, 0.0]
        assert line.end == [1.0, 1.0]
        assert line.layer == 'layer'
        assert Line.parse(line.to_string()) == line


class PolygonTests(unittest.TestCase):
    def test_polygon(self):
        poly = Polygon.parse('(fp_poly (pts (xy 0 0) (xy 1 0)) (width 0.01))')
        assert poly.pts == [(0, 0), (1, 0)]
        assert poly.width == 0.01
        assert Polygon.parse(poly.to_string()) == poly


class CurveTests(unittest.TestCase):
    def test_curve(self):
        curve = Curve.parse(
            '(fp_curve (pts (xy 0 0) (xy 1 1) (xy 2 2) (xy 3 3)))')
        assert curve.start == (0, 0)
        assert curve.bezier1 == (1, 1)
        assert curve.bezier2 == (2, 2)
        assert curve.end == (3, 3)


class ModelTests(unittest.TestCase):
    def test_model(self):
        model_string = (
            '(model path'
            '    (at (xyz 10 0 0))'
            '    (scale (xyz 0 0 0))'
            '    (rotate (xyz 0 0 0)))')
        model = Model.parse(model_string)
        assert model.at == (10, 0, 0)
        assert model.scale == (0, 0, 0)
        assert model.rotate == (0, 0, 0)
        assert Model.parse(model.to_string()) == model


class ModuleTests(unittest.TestCase):
    def test_module(self):
        module_string = '(module name (layer F.Cu) %s)'
        module = Module.parse(module_string % '')
        assert module.name == 'name'
        assert module.layer == 'F.Cu'
        assert Module.parse(module.to_string()) == module

        pads = ''
        for i in range(2):
            pads += Pad(str(i + 1), drill=Drill(0.8)).to_string()

        module = Module.parse(module_string % pads)
        assert module.pads[0].name == '1'
        assert module.pads[0].drill.size == 0.8
        assert module.pads[1].name == '2'
        assert module.pads[1].drill.size == 0.8
        assert Module.parse(module.to_string()) == module


class NetTests(unittest.TestCase):
    def test_net_auto_numbering(self):
        n1, n2, n3 = Net(), Net(), Net()
        assert n1.code == 1
        assert n2.code == 2
        assert n3.code == 3
