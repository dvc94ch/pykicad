from pyparsing import *
from functools import reduce


text = dblQuotedString | Word(printables + alphas8bit, excludeChars=')')
yes_no = Literal('yes') | 'no'
boolean = Literal('true') | 'false'
number = Combine(Optional('-') + Word(nums) + Optional(Word('.') + Word(nums)))
integer = Word(nums)
hex = Word(hexnums)

dblQuotedString.setParseAction(removeQuotes)
number.setParseAction(lambda tokens: float(tokens[0]))
integer.setParseAction(lambda tokens: int(tokens[0]))
yes_no.setParseAction(lambda tokens: True if tokens[0] == 'yes' else False)
boolean.setParseAction(lambda tokens: True if tokens[0] == 'true' else False)


# Python 2 compatibility
try:
  basestring
except NameError:
  basestring = str


def flag(name):
    return {
        '_parser': Literal(name).setParseAction(lambda x: True),
        '_printer': lambda flag: name if flag else '',
        '_tag': False,
        '_attr': name
    }


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


def reduce_parser_list(parsers, func):
    if isinstance(parsers, list) and len(parsers) > 0:
        return reduce(func, parsers)
    return Empty()

def sexpr(name, positional=None, single=None, multiple=None):
    if isinstance(positional, ParserElement):
        parser = positional
    else:
        positional = reduce_parser_list(positional, lambda x, y: x + y)
        single = reduce_parser_list(single, lambda x, y: x & y)
        multiple = reduce_parser_list(multiple, lambda x, y: x & y)
        parser = positional + single + multiple

    name = Empty() if name == '' else Suppress(name)
    return Suppress('(') + name + parser + Suppress(')')


def generate_parser(tag, schema, attr=None, optional=False):
    '''A schema is either a ParserElement, a AST subclass or a dict.  When
    a dict contains a _parser key it is a leaf.

    A leaf has an _attr name.  When no _attr name is given explicitly it
    defaults to using the tag name.
    '''

    def leaf(parser, attr):
        return Group(parser).setParseAction(leaf_parse_action(attr))

    def ast(ast, attr):
        return Group(ast.parser()).setParseAction(ast_parse_action(attr, ast))


    # Case 1: schema is a ParserElement
    if isinstance(schema, ParserElement):
        parser = schema

        if isinstance(tag, basestring):
            # The tag is a string so the leaf is an sexpr.
            parser = sexpr(tag, parser)

        # Default to using the tag as the attr value
        if attr is None:
            attr = tag

        # Assert that attr is a string, if it is not
        # something is terribly wrong.
        assert isinstance(attr, basestring)

        # Apply the default leaf parse action.
        parser = leaf(parser, attr)

        # Make it optional if necessary
        if optional:
            parser = Optional(parser)

        return parser


    # Case 2: schema is a subclass of AST
    if type(schema) == type and issubclass(schema, AST):

        if attr is None:
            attr = tag

        assert isinstance(attr, basestring)

        parser = ast(schema, attr)

        if optional:
            parser = Optional(parser)

        return parser


    # Case 3: schema is a dict or something is wrong
    assert isinstance(schema, dict)


    # Subcase 1: schema is a leaf node
    if '_parser' in schema:
        parser = schema['_parser']

        # Something is wrong if parser is a dict
        assert not isinstance(parser, dict)

        tag = schema.get('_tag', tag)
        attr = schema.get('_attr', tag)
        parser = generate_parser(tag, parser, attr)
    # Subcase 2: schema is not a leaf node
    else:
        # Determine positional arguments. Positional arguments are
        # arguments that are required to be in a certain position within
        # an sexpression. They are by default required.
        i, positional = 0, []
        while str(i) in schema:
            # Default tag to False for positional arguments. Positional arguments
            # are required to have an _attr, _tag key or have a subschema.
            positional.append(generate_parser(tag=False, schema=schema[str(i)],
                                              attr=None, optional=False))
            i += 1

        # Determine the rest of the arguments. Here the position doesn't matter
        # within the sexpr. These default to being optional.
        single = []
        multiple = []
        for key, value in schema.items():
            # A key is either a number representing a positional argument a
            # special key starting with an underscore or a subschema.
            if not (key.isdigit() or key[0] == '_'):
                # Tags that have _multiple set need to go after those that don't
                if isinstance(value, dict) and '_multiple' in value:
                    children = multiple
                else:
                    children = single
                children.append(generate_parser(tag=key, schema=value,
                                                attr=None, optional=True))

        parser = sexpr(tag, positional, single, multiple)

    if schema.get('_multiple', False):
        parser = ZeroOrMore(parser)
    elif schema.get('_optional', optional):
        parser = Optional(parser)

    return parser


def find_attr(attr, value, schema):
    def is_leaf_node(schema):
        if not isinstance(schema, dict):
            return True
        if '_parser' in schema:
            return True
        return False

    def printer(schema):
        def closure(printer):
            return (lambda value: ' '.join(map(printer, value))
                    if isinstance(value, list) else printer(value))

        if type(schema) == type:
            return schema.to_string

        if not isinstance(schema, dict):
            return False

        printer = False
        parser = schema.get('_parser', False)
        if type(parser) == type and issubclass(parser, AST):
            printer = parser.to_string

        printer = schema.get('_printer', printer)

        if schema.get('_multiple', False):
            printer = closure(printer)

        return printer


    # Case 1: Schema is a leaf node
    if is_leaf_node(schema):
        if not isinstance(schema, dict):
            return None

        if schema.get('_attr', schema.get('_tag', False)) == attr:
            printer = printer(schema)
            if printer:
                value = ('_', printer(value))

            if schema.get('_tag', False):
                value = {schema['_tag']: value}

            return value

        return None


    # Case 2: Subschema is a leaf node and the schema does not
    # overwrite the _attr.
    if attr in schema and is_leaf_node(schema[attr]) and \
       (not isinstance(schema[attr], dict) or
        (schema[attr].get('_attr', attr) == attr)):

        subschema = schema[attr]
        tag = attr

        if isinstance(subschema, dict):
            tag = subschema.get('_tag', tag)

        printer = printer(subschema)
        if printer:
            value = printer(value)
            tag = '_' + attr

        return {tag: value}


    # Default: Search in subschemas
    for key, subschema in schema.items():
        if key[0] == '_':
            continue

        found = find_attr(attr, value, subschema)
        if not found is None:
            return {key: found}

    return None


def tree_to_string(tree, level=0):
    if isinstance(tree, basestring):
        if tree == '':
            return '""'
        if ' ' in tree or '(' in tree or ')' in tree:
            return '"%s"' % tree
        return tree
    if isinstance(tree, tuple):
        a, b = tree
        return b
    if isinstance(tree, bool):
        return 'yes' if tree else 'no'
    if isinstance(tree, float):
        return '%.10f' % tree
    if isinstance(tree, int):
        return str(tree)
    if isinstance(tree, list):
        return ' '.join(map(tree_to_string, tree))
    if isinstance(tree, AST):
        return tree.to_string()

    assert isinstance(tree, dict)

    i, pos = 0, []
    while str(i) in tree:
        pos.append(tree_to_string(tree[str(i)], level))
        i += 1

    single = []
    multiple = []
    for key, value in tree.items():
        if len(key) > 0 and key[0] == '_':
            if not value == '':
                multiple.append(value)
        elif not key.isdigit():
            value = tree_to_string(value, level + 1)
            if not value == '':
                single.append('\n%s(%s %s)' % (level * '    ', key, value))

    return ' '.join(pos + single + multiple)


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
            super(AST, self).__setattr__(attr, value)

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
            tree = self.attributes
        else:
            tree = {self.tag: tree}

        return tree_to_string(tree)

    def init_list(self, arg, default):
        '''Helper to initialize lists. Since default arguments are initialized
        at import time and lists are reference types, all lists of all instances
        point to the same list.'''

        if arg is None:
            return default
        if not isinstance(arg, list):
            return [arg]
        return arg

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
