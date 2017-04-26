import unittest
from pytest import *
from pykicad.pcb import *


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
