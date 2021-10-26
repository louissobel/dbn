from collections import namedtuple

class ProcedureDefinition(object):
    def __init__(self, node, name, args, is_number):
        self.node = node
        self.name = name
        self.args = args
        self.is_number = is_number
        self.label = None
        self.block_dependencies = None

        self.stack_args = None
        self.local_env_args = None

    def __repr__(self):
        return "<%s %s (%s) @%s>" % (
            'Number' if self.is_number else 'Command',
            self.name,
            ', '.join(self.args),
            '[uncompiled]' if self.label is None else self.label,
        )

class BlockDependencies(object):
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
        return "<BlockDependencies gets:%s sets:%s calls:%s>" % (
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
            for get in dfn.block_dependencies.variable_gets:
                if get.is_global:
                    expected.add(get.symbol)
            expected |= dfn.block_dependencies.globals_expected_by_any_called_function(procedure_definitions_by_name, seen)

        return expected

    def is_stack_eligible(self, symbol, procedure_definitions_by_name, shift_stack=0):
        expected_globals = self.globals_expected_by_any_called_function(
            procedure_definitions_by_name,
        )
        if symbol in expected_globals:
            return False

        gets = [a for a in self.variable_gets if a.symbol == symbol]
        sets = [a for a in self.variable_sets if a.symbol == symbol]

        deepest_get = max(gets, key=lambda a : a.stack_size).stack_size + shift_stack if gets else None 
        deepest_set = max(sets, key=lambda a : a.stack_size).stack_size + shift_stack if sets else None

        return (
            (deepest_set is None or deepest_set < 17)
            and (deepest_get is None or deepest_get < 16)
        )

Metadata = namedtuple('Metadata', ['owning_contract', 'description'])
EMPTY_METADATA = Metadata(None, None)

class SymbolDirectory(object):
    """
    Compiler uses this to keep track of where various symbols can be found
    (local env, stack, etc)
    """
    LOCAL_ENV = object()
    GLOBAL = object()
    STACK = object()

    class SymbolLocation(object):

        def __init__(self, location, slot=None):
            self.location = location
            self.slot = slot

            if self.slot and not location == SymbolDirectory.STACK:
                raise ValueError("only Stack location has slot")

        def __repr__(self):
            if self.location == SymbolDirectory.LOCAL_ENV:
                return "<Local>"
            elif self.location == SymbolDirectory.STACK:
                return "<Stack %d>" % self.slot
            else:
                return "<Unknown>"

        def is_local(self):
            return self.location == SymbolDirectory.LOCAL_ENV

        def is_stack(self):
            return self.location == SymbolDirectory.STACK

        def is_global(self):
            return self.location == SymbolDirectory.GLOBAL

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
            self.SymbolLocation(self.GLOBAL),
        )

    def copy(self):
        return self.__class__(self.symbol_mapping)

    def set_local(self, symbol):
        """
        mutates!
        """
        self.symbol_mapping[symbol] = self.SymbolLocation(self.LOCAL_ENV)

    def set_stack(self, symbol, slot):
        """
        mutates!
        """
        self.symbol_mapping[symbol] = self.SymbolLocation(self.STACK, slot)

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

