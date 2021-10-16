

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
