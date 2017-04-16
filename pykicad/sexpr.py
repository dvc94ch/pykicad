from pyparsing import *
from functools import reduce


text = dblQuotedString | Word(printables + alphas8bit, excludeChars=')')
number = Combine(Optional('-') + Word(nums) + Optional(Word('.') + Word(nums)))

dblQuotedString.setParseAction(removeQuotes)
number.setParseAction(lambda tokens: float(tokens[0]))


def parse_action(tokens):
    if len(tokens) < 2:
        return tokens[0]
    if isinstance(tokens[0], float):
        return list(tokens)
    if isinstance(tokens[0], dict):
        res = {}
        for token in tokens:
            res.update(token)
        return res


def leaf_parse_action(name):
    def action(tokens):
        return {name: parse_action(tokens[0])}

    return action


def ast_parse_action(name, ast):
    def action(tokens=None):
        if tokens is None:
            return
        return {name: ast(**parse_action(tokens[0]))}

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


def generate_parser(name, schema):
    def leaf(parser, name):
        return Group(parser).setParseAction(leaf_parse_action(name))

    def ast(ast, name):
        return Group(ast.parser()).setParseAction(ast_parse_action(name, ast))

    def node(parser):
        return Group(parser).setParseAction(parse_action)

    if isinstance(schema, ParserElement):
        return leaf(sexpr(name, schema), name)

    if '_parser' in schema:
        parser = schema['_parser']
        if isinstance(parser, ParserElement):
            if schema.get('_tag', True):
                parser = leaf(sexpr(name, parser), name)
        elif issubclass(parser, AST):
            parser = ast(parser, name)
    else:
        i, positional = 0, []
        while str(i) in schema:
            _parser = schema[str(i)]['_parser']
            _attr = schema[str(i)]['_attr']
            _parser = leaf(_parser, _attr)
            positional.append(_parser)
            i += 1

        children = []
        for key, value in schema.items():
            if not (key.isdigit() or key[0] == '_'):
                children.append(generate_parser(key, value))

        parser = sexpr(name, positional, children)

    if schema.get('_multiple', False):
        parser = ZeroOrMore(parser)
    elif schema.get('_optional', False):
        parser = Optional(parser)

    return parser


def find_attr(attr, value, schema):
    if not isinstance(schema, dict):
        return None

    if '_attr' in schema and schema['_attr'] == attr:
        if '_printer' in schema:
            value = ('_', schema['_printer'](value))
        return value

    if attr in schema:
        if isinstance(schema[attr], dict) and '_printer' in schema[attr]:
            printer = schema[attr]['_printer']
            attr = '_' + attr
            if isinstance(value, list):
                value = ' '.join(map(printer, value))
            else:
                value = printer(value)

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
        return '%f' % tree
    if isinstance(tree, list):
        return ' '.join(map(tree_to_string, tree))
    if issubclass(type(tree), AST):
        return tree.to_string()

    i, pos = 0, []
    while str(i) in tree:
        pos.append(tree_to_string(tree[str(i)]))
        i += 1

    children = []
    for key, value in tree.items():
        if key[0] == '_':
            children.append('\n'.join(map(lambda x: level * '    ' + x,
                                          value.split('\n'))))
        elif not key.isdigit():
            children.append('\n%s(%s %s)' % (level * '    ', key, tree_to_string(value, level + 1)))

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

    def __eq__(self, other):
        return self.attributes == other.attributes

    def __repr__(self):
        attrs = {}
        for key, value in self.attributes.items():
            if value is not None:
                attrs[key] = value
        return '(%s %s)' % (self.tag, repr(attrs))

    def to_string(self, attributes=None):
        if attributes is None:
            attributes = self.attributes

        tree = {}
        for attr, value in attributes.items():
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
