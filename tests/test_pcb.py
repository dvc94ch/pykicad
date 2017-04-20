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
