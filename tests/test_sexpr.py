import unittest
from pytest import *
from pyparsing import ParseException
from pykicad.sexpr import *
from pykicad.module import Drill

class ASTTests(unittest.TestCase):
    def test_unicode(self):
        AST.from_schema('sexpr', text)
        ast = AST.parse('(sexpr ü)')
        assert ast.sexpr == 'ü'
        assert AST.parse(ast.to_string()) == ast

    def test_simple_leaf_tag(self):
        AST.from_schema('sexpr', number)
        ast = AST.parse('(sexpr 1)')
        assert ast.sexpr == 1.0
        assert AST.parse(ast.to_string()) == ast

    def test_composite_leaf_tag(self):
        AST.from_schema('sexpr', number + number)
        ast = AST.parse('(sexpr 1 2)')
        assert ast.sexpr == [1, 2]
        assert AST.parse(ast.to_string()) == ast

    def test_nested_tags(self):
        AST.from_schema('sexpr', {'sexpr': number})
        ast = AST.parse('(sexpr (sexpr 1))')
        assert ast.sexpr == 1.0
        assert AST.parse(ast.to_string()) == ast

    def test_nested_tags_with_composite_leaf(self):
        AST.from_schema('sexpr', {'sexpr': number + number})
        ast = AST.parse('(sexpr (sexpr 1 2))')
        assert ast.sexpr == [1, 2]
        assert AST.parse(ast.to_string()) == ast

    def test_multiple_nested_tags(self):
        AST.from_schema('sexpr', {'zero': number, 'one': number})
        ast = AST.parse('(sexpr (zero 0) (one 1))')
        assert ast.zero == 0.0
        assert ast.one == 1.0
        assert AST.parse(ast.to_string()) == ast

    def test_tag_with_explicit_parser_attr(self):
        AST.from_schema('sexpr', {'_parser': number})
        ast = AST.parse('(sexpr 1)')
        assert ast.sexpr == 1.0
        assert AST.parse(ast.to_string()) == ast

    def test_tag_with_named_positional(self):
        AST.from_schema('sexpr', {
            '0': {
                '_attr': 'zero',
                '_parser': number
            }
        })
        ast = AST.parse('(sexpr 1)')
        assert ast.zero == 1.0
        assert AST.parse(ast.to_string()) == ast

    def test_tag_with_multiple_named_positional(self):
        AST.from_schema('sexpr', {
            '0': {
                '_attr': 'zero',
                '_parser': number
            },
            '1': {
                '_attr': 'one',
                '_parser': number
            }
        })
        ast = AST.parse('(sexpr 0 1)')
        assert ast.zero == 0.0
        assert ast.one == 1.0
        assert AST.parse(ast.to_string()) == ast

    def test_optional_tag(self):
        AST.from_schema('sexpr', {
            '0': {
                '_attr': 'zero',
                '_parser': number
            },
            'sexpr': {
                '_parser': number,
                '_optional': True
            }
        })
        ast = AST.parse('(sexpr 1)')
        assert ast.zero == 1.0
        ast = AST.parse('(sexpr 1 (sexpr 2))')
        assert ast.zero == 1.0
        assert ast.sexpr == 2.0
        assert AST.parse(ast.to_string()) == ast

    def test_ast(self):
        AST.from_schema('pad', {
            'drill': {
                '_parser': Drill,
                '_printer': Drill.to_string
            }
        })
        ast = AST.parse('(pad (drill 0.8))')
        assert isinstance(ast.drill, Drill)
        assert ast.drill.size == 0.8
        assert AST.parse(ast.to_string()) == ast

    def test_multiple(self):
        AST.from_schema('sexpr', {
            'drills': {
                '_parser': Drill,
                '_printer': Drill.to_string,
                '_multiple': True,
                '_optional': True
            }
        })
        ast = AST.parse('(sexpr (drill 0.8) (drill 0.6))')
        assert ast.drills[0].size == 0.8
        assert ast.drills[1].size == 0.6
        assert AST.parse(ast.to_string()) == ast

        ast = AST.parse('(sexpr (drill 0.8))')
        assert ast.drills.size == 0.8
        assert AST.parse(ast.to_string()) == ast

    def test_multiple_multiple(self):
        AST.from_schema('sexpr', {
            'drills': {
                '_parser': Drill,
                '_printer': Drill.to_string,
                '_multiple': True,
            },
            'pad': {
                '_parser': number,
            }
        })
        ast = AST.parse('(sexpr (drill 1) (pad 1) (drill 2) (drill 3))')
        assert ast.pad == 1.0
        assert ast.drills[0].size == 1.0
        assert ast.drills[1].size == 2.0
        assert ast.drills[2].size == 3.0
        assert AST.parse(ast.to_string()) == ast

    def test_positional_sexpr(self):
        AST.from_schema('sexpr', {
            '0': {
                '_tag': 'start',
                '_parser': number + number,
            },
            '1': {
                '_tag': 'end',
                '_parser': number + number
            }
        })
        ast = AST.parse('(sexpr (start 1 1) (end 2 2))')
        assert ast.start == [1.0, 1.0]
        assert ast.end == [2.0, 2.0]
        assert AST.parse(ast.to_string()) == ast

        with raises(ParseException):
            AST.parse('(sexpr (end 2 2) (start 1 1))')

    def test_tag_and_attr_schema(self):
        AST.from_schema('sexpr', {
            '0': {
                '_tag': 'sexpr2',
                '_attr': 'attr',
                '_parser': number
            }
        })
        ast = AST.parse('(sexpr (sexpr2 1))')
        assert ast.attr == 1.0
        assert AST.parse(ast.to_string()) == ast

    def test_positional_ast(self):
        AST.from_schema('sexpr', {
            '0': {
                '_attr': 'drill',
                '_parser': Drill,
                '_printer': Drill.to_string
            }
        })
        ast = AST.parse('(sexpr (drill 0.8))')
        assert ast.drill.size == 0.8
        assert AST.parse(ast.to_string()) == ast

    def test_positional_multiple_ast(self):
        AST.from_schema('sexpr', {
            '0': {
                '_attr': 'drills',
                '_parser': Drill,
                '_printer': Drill.to_string,
                '_multiple': True
            }
        })
        ast = AST.parse('(sexpr (drill 0.6) (drill 0.8))')
        assert len(ast.drills) == 2
        assert AST.parse(ast.to_string()) == ast
