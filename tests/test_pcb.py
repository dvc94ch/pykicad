import unittest
from pytest import *
from pykicad.pcb import *


class NetClassTests(unittest.TestCase):
    def test_parse(self):
        nc_string = "(net_class name description (add_net GND))"
        nc = NetClass.parse(nc_string)
        assert nc.name == 'name'
        assert nc.description == 'description'
        assert nc.nets == ['GND']

    def test_without_net(self):
        nc = NetClass('default')
        assert NetClass.parse(nc.to_string()) == nc

    def test_with_net(self):
        nc = NetClass('default')
        nc.nets.append('GND')
        assert NetClass.parse(nc.to_string()) == nc

    def test_with_multiple_nets(self):
        nc = NetClass('default')
        nc.nets += ['GND', 'VO']
        nc_str = nc.to_string()
        assert NetClass.parse(nc.to_string()) == nc


class PcbTests(unittest.TestCase):
    def test_minimal_pcb(self):
        pcb_string = open('tests/minimal_pcb.kicad_pcb', 'r').read()
        pcb = Pcb.parse(pcb_string)
        assert pcb.version == 123
        assert pcb.host == ['pcbnew', 'version']
        assert len(pcb.nets) == 4
        assert len(pcb.modules) == 2
        assert Pcb.parse(pcb.to_string()) == pcb

    def test_page(self):
        pcb = Pcb()
        assert Pcb.parse(pcb.to_string()) == pcb
        pcb.page_type = 'A4'
        assert Pcb.parse(pcb.to_string()) == pcb
        pcb.page_type = [200, 200]
        assert Pcb.parse(pcb.to_string()) == pcb

    def test_single_module(self):
        pcb = Pcb()
        pcb.modules.append(Module(name='R'))
        assert Pcb.parse(pcb.to_string()) == pcb

    def test_comment(self):
        pcb = Pcb(comment1='hello world', comment2='bye world')
        assert Pcb.parse(pcb.to_string()) == pcb

    def test_num_nets(self):
        pcb = Pcb(num_nets=5)
        assert Pcb.parse(pcb.to_string()) == pcb
        pcb.nets.append(Net())
        assert Pcb.parse(pcb.to_string()) == pcb

    def test_layers(self):
        pcb = Pcb()
        pcb.layers.append(Layer('B.Cu'))
        assert Pcb.parse(pcb.to_string()) == pcb
        pcb.layers.append(Layer('F.Cu'))
        assert Pcb.parse(pcb.to_string()) == pcb
