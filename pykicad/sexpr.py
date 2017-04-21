from pyparsing import *
from functools import reduce


text = dblQuotedString | Word(printables + alphas8bit, excludeChars=')')
number = Combine(Optional('-') + Word(nums) + Optional(Word('.') + Word(nums)))
integer = Word(nums)

dblQuotedString.setParseAction(removeQuotes)
number.setParseAction(lambda tokens: float(tokens[0]))
integer.setParseAction(lambda tokens: int(tokens[0]))


def parse_action(tokens):
    if len(tokens) < 2:
        return tokens[0]
    if isinstance(tokens[0], dict):
        res = {}
        for token in tokens:
            res.update(token)
        return res
    return list(tokens)


def leaf_parse_action(attr):
    def action(tokens):
        return {attr: parse_action(tokens[0])}

    return action


def ast_parse_action(attr, ast):
    def action(tokens=None):
        if tokens is None:
            return
        return {attr: ast(**parse_action(tokens[0]))}

    return action


def sexpr(name, positional=None, children=None):
    if isinstance(positional, ParserElement):
        parser = positional
    else:
        if isinstance(positional, list):
            if len(positional) > 0:
                parser = reduce(lambda x, y: x + y, positional)
            else:
                parser = None
        if isinstance(children, list):
            if len(children) > 0:
                children = reduce(lambda x, y: x & y, children)
                if parser is None:
                    parser = children
                else:
                    parser += children

    return Suppress('(') + Suppress(name) + parser + Suppress(')')


def generate_parser(tag, schema, attr=None):
    def leaf(parser, attr):
        return Group(parser).setParseAction(leaf_parse_action(attr))

    def ast(ast, attr):
        return Group(ast.parser()).setParseAction(ast_parse_action(attr, ast))

    if isinstance(schema, ParserElement):
        parser = schema
        if isinstance(tag, str):
            parser = sexpr(tag, parser)
        if attr is None:
            attr = tag
        assert isinstance(attr, str)
        return leaf(parser, attr)

    if type(schema) == type and issubclass(schema, AST):
        return ast(schema, attr)


    if '_parser' in schema:
        parser = schema['_parser']
        tag = schema.get('_tag', tag)
        attr = schema.get('_attr', tag)
        parser = generate_parser(tag, parser, attr)
    else:
        i, positional = 0, []
        while str(i) in schema:
            positional.append(generate_parser(False, schema[str(i)]))
            i += 1

        children = []
        for key, value in schema.items():
            if not (key.isdigit() or key[0] == '_'):
                children.append(generate_parser(key, value))

        parser = sexpr(tag, positional, children)

    if schema.get('_multiple', False):
        parser = ZeroOrMore(parser)
    elif schema.get('_optional', False):
        parser = Optional(parser)

    return parser


def find_attr(attr, value, schema):
    def printer(printer, value, multiple):
        if multiple and isinstance(value, list):
            return ' '.join(map(printer, value))
        return printer(value)

    if not isinstance(schema, dict):
        return None

    if schema.get('_attr', schema.get('_tag', False)) == attr:
        if '_printer' in schema:
            value = ('_', printer(schema['_printer'], value,
                                  schema.get('_multiple', False)))

        if schema.get('_tag', False):
            return {schema['_tag']: value}
        return value

    if attr in schema:
        if isinstance(schema[attr], dict) and '_printer' in schema[attr]:
            value = printer(schema[attr]['_printer'], value,
                            schema[attr].get('_multiple', False))
            attr = '_' + attr

        return {attr: value}

    for key, subschema in schema.items():
        if key[0] == '_':
            continue

        found = find_attr(attr, value, subschema)
        if not found is None:
            return {key: found}

    return None


def tree_to_string(tree, level=0):
    if isinstance(tree, str):
        if tree == '':
            return '""'
        if ' ' in tree or '(' in tree or ')' in tree:
            return '"%s"' % tree
        return tree
    if isinstance(tree, tuple):
        a, b = tree
        return b
    if isinstance(tree, float):
        return '%.10f' % tree
    if isinstance(tree, int):
        return str(tree)
    if isinstance(tree, list):
        return ' '.join(map(tree_to_string, tree))
    if issubclass(type(tree), AST):
        return tree.to_string()

    i, pos = 0, []
    while str(i) in tree:
        pos.append(tree_to_string(tree[str(i)], level))
        i += 1

    children = []
    for key, value in tree.items():
        if key[0] == '_':
            children.append(value)
        elif not key.isdigit():
            children.append('\n%s(%s %s)' % (level * '    ', key,
                                             tree_to_string(value, level + 1)))

    return ' '.join(pos + children)


def merge_dict(d1, d2):
    """Assume that if there is a key conflict, there is a nested dict."""

    for key, value in d2.items():
        if key in d1:
            merge_dict(d1[key], value)
        else:
            d1[key] = value


class AST(object):
    tag = 'sexpr'
    schema = text

    def __init__(self, **kwargs):
        self.attributes = kwargs

    def __getattr__(self, attr):
        try:
            return self.attributes.get(attr)
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, attr, value):
        if not attr == 'attributes' and attr in self.attributes:
            self.attributes[attr] = value
        else:
            super().__setattr__(attr, value)

    def __eq__(self, other):
        return self.attributes == other.attributes

    def __repr__(self):
        attrs = {}
        for key, value in self.attributes.items():
            if value is not None:
                attrs[key] = value
        return '(%s %s)' % (self.tag, repr(attrs))

    def __str__(self):
        return self.to_string()[1:] + '\n'

    def to_string(self, attributes=None):
        if attributes is None:
            attributes = self.attributes.items()

        tree = {}
        for attr, value in attributes:
            if value is None:
                continue

            found = find_attr(attr, value, self.schema)
            if found is None:
                continue

            merge_dict(tree, found)

        if tree == {}:
            tree = attributes
        else:
            tree = {self.tag: tree}

        return tree_to_string(tree)

    @classmethod
    def parser(cls):
        return generate_parser(cls.tag, cls.schema)

    @classmethod
    def parse(cls, string):
        if not hasattr(cls, '_parser'):
            cls._parser = generate_parser(cls.tag, cls.schema)

        parse_result = cls._parser.parseString(string)

        result = {}
        for res in parse_result:
            if len(list(res.keys())) < 1:
                continue

            key = next(iter(res.keys()))
            if not key in result:
                result.update(res)
            else:
                if not isinstance(result[key], list):
                    result[key] = [result[key]]
                result[key].append(res[key])

        return cls(**result)

    @classmethod
    def from_schema(cls, tag, schema):
        """Only for testing purposes."""

        cls.tag = tag
        cls.schema = schema
        cls._parser = generate_parser(tag, schema)
        return cls
