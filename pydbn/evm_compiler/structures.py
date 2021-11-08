import sys
from collections import namedtuple

class CompileError(ValueError):
    def __init__(self, message, line, related_line=None, line_number_in_message=False):
        super().__init__(message)

        self.message = message
        self.line = line
        self.related_line = related_line
        self.line_number_in_message = line_number_in_message

class ProcedureDefinition(object):
    StackSlot = namedtuple('StackSlot', ['is_arg', 'symbol'])

    def __init__(self, node, name, args, is_number):
        self.node = node
        self.name = name
        self.args = args
        self.is_number = is_number

        self.label = None
        self.epilogue_label = None
        self.scope_dependencies = None

        self.stack_slots = []
        self.local_env_args = args
        self.needs_env = True

    def __repr__(self):
        return "<%s %s (%s) @%s>" % (
            'Number' if self.is_number else 'Command',
            self.name,
            ', '.join(self.args),
            '[uncompiled]' if self.label is None else self.label,
        )

class ScopeDependencies(object):
    VariableAccess = namedtuple('VariableAccess', [
        'symbol',
        'stack_size',
        'is_global',
        'line_no'
    ])
    def __init__(self):
        self.variable_gets = []
        self.variable_sets = []
        self.procedures_called = []

    def __repr__(self):
        return "<ScopeDependencies gets:%s sets:%s calls:%s>" % (
            self.variable_gets,
            self.variable_sets,
            self.procedures_called,
        )

    def globals_expected_by_any_called_function(self, procedure_definitions_by_name, seen=None):
        if seen is None:
            seen = set()

        expected = set()

        for call in self.procedures_called:
            # TODO: better error message?
            if call.symbol in seen:
                continue
            seen.add(call.symbol)

            dfn = procedure_definitions_by_name[call.symbol]
            for get in dfn.scope_dependencies.variable_gets:
                if get.is_global:
                    expected.add(get.symbol)
            expected |= dfn.scope_dependencies.globals_expected_by_any_called_function(procedure_definitions_by_name, seen)

        return expected

Metadata = namedtuple('Metadata', ['helper_address', 'description'])
EMPTY_METADATA = Metadata(None, None)

class SymbolDirectory(object):
    """
    Compiler uses this to keep track of where various symbols can be found
    (local env, stack, etc)
    """

    class SymbolLocation(object):
        LOCAL_ENV = object()
        GLOBAL = object()
        STACK = object()

        @classmethod
        def local(cls):
            return cls(cls.LOCAL_ENV)

        @classmethod
        def _global(cls):
            return cls(cls.GLOBAL)

        @classmethod
        def stack(cls, slot):
            return cls(cls.STACK, slot)

        def __init__(self, location, slot=None):
            self.location = location
            self.slot = slot

            if self.slot and not location == self.STACK:
                raise ValueError("only Stack location has slot")

        def __repr__(self):
            if self.location == self.LOCAL_ENV:
                return "<Local>"
            elif self.location == self.STACK:
                return "<Stack %d>" % self.slot
            else:
                return "<Unknown>"

        def is_local(self):
            return self.location == self.LOCAL_ENV

        def is_stack(self):
            return self.location == self.STACK

        def is_global(self):
            return self.location == self.GLOBAL

    def __init__(self, initial_mapping=None):
        if initial_mapping:
            self.symbol_mapping = initial_mapping
        else:
            self.symbol_mapping = {}

    def __repr__(self):
        return "SymbolDirectory(" + repr(self.symbol_mapping) + ")"

    def all_locals(self):
        return {k for k, v in self.symbol_mapping.items() if v.is_local()}

    def location_for(self, symbol):
        return self.symbol_mapping.get(
            symbol,
            self.SymbolLocation._global(),
        )

    def copy(self):
        return self.__class__(self.symbol_mapping)

    def set_local(self, symbol):
        """
        mutates!
        """
        self.symbol_mapping[symbol] = self.SymbolLocation.local()

    def set_stack(self, symbol, slot):
        """
        mutates!
        """
        self.symbol_mapping[symbol] = self.SymbolLocation.stack(slot)

    def with_local(self, symbol):
        c = self.copy()
        c.set_local(symbol)
        return c

    def with_locals(self, locals):
        c = self.copy()
        for s in locals:
            c.set_local(s)
        return c

    def with_stack(self, stack_slots):
        c = self.copy()
        for s, i in stack_slots.items():
            c.set_stack(s, i)
        return c

    def with_locations(self, mapping):
        c = self.copy()
        for s, l in mapping.items():
            c.symbol_mapping[s] = l
        return c


BuiltinProcedure = namedtuple('BuiltinProcedure', [
    'name',
    'procedure_type',
    'argc',
    'handler',
])


LinkedFunction = namedtuple('LinkedFunction', [
    'label',
])

class LinkedFunctions:
    DOT_GET = LinkedFunction('dotGet')
    SET_COMMAND = LinkedFunction('setCommand')
    LINE_COMMAND = LinkedFunction('lineCommand')
    PAPER_COMMAND = LinkedFunction('paperCommand')
    ENV_GET = LinkedFunction('envGet')
    TIME_NUMBER = LinkedFunction('timeNumber')
