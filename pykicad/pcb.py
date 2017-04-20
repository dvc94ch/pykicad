from pykicad.sexpr import *
from pykicad.module import Module, Net


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
            '_printer': Net.to_string,
            '_multiple': True
        },
        'modules': {
            '_parser': Module,
            '_printer': Module.to_string,
            '_multiple': True
        }
    }

    def __init__(self, version=1, host=['pykicad', 'x.x.x'], nets=[], modules=[]):
        super().__init__(version=version, host=host, nets=nets, modules=modules)
