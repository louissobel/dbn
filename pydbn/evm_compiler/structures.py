from collections import namedtuple

class ProcedureDefinition(object):
    def __init__(self, name, args, is_number):
        self.name = name
        self.args = args
        self.is_number = is_number
        self.label = None

    def __repr__(self):
        return "<%s %s (%s) @%s>" % (
            'Number' if self.is_number else 'Command',
            self.name,
            ', '.join(self.args),
            '[uncompiled]' if self.label is None else self.label,
        )


Metadata = namedtuple('Metadata', ['owning_contract', 'description'])
EMPTY_METADATA = Metadata(None, None)




class SymbolDirectory(object):
    """
    Compiler uses this to keep track of where various symbols can be found
    (local env, stack, etc)
    """
    LOCAL_ENV = object()
    UNKNOWN = object()

    class SymbolLocation(object):

        def __init__(self, location):
            self.location = location

        def __repr__(self):
            if self.location == SymbolDirectory.LOCAL_ENV:
                return "<Local>"
            else:
                return "<Unknown>"

        def is_local(self):
            return self.location == SymbolDirectory.LOCAL_ENV

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
            self.SymbolLocation(self.UNKNOWN),
        )

    def copy(self):
        return self.__class__(self.symbol_mapping)

    def set_local(self, symbol):
        """
        mutates!
        """
        self.symbol_mapping[symbol] = self.SymbolLocation(self.LOCAL_ENV)

    def with_local(self, symbol):
        c = self.copy()
        c.set_local(symbol)
        return c

    @classmethod
    def with_locals(cls, locals):
        return cls({s: cls.SymbolLocation(cls.LOCAL_ENV) for s in locals})

