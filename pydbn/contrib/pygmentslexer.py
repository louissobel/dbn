from pygments.lexer import Lexer
from pygments.token import *
from pygments.style import Style

from parser import DBNTokenizer

class DBNLexer(Lexer):
    name = 'DBN',
    aliases= ['dbn']
    filenames = ['*.dbn']

    def __init__(self, *args, **kwargs):
        Lexer.__init__(self, *args, **kwargs)
        self.tokenizer = DBNTokenizer(filter=False)

    def get_tokens(self, text):
        tokens = self.tokenizer.tokenize(text)
        state = 'root'

        out = []
        for token in tokens:
            type_, next_state = self.translate(token, state)
            out.append((type_, unicode(token.raw)))
            state = next_state
        return out

    def translate(self, token, state):
        type_map = self.translations[state]
        for type_type_state in type_map:
            if len(type_type_state) == 2:
                source, pygme = type_type_state
                next_state = state
            else:
                source, pygme, next_state = type_type_state

            if isinstance(source, tuple):
                match = token.type in source
            else:
                match = token.type == source

            if match:
                return pygme, next_state

        # Fallback to error if we can't find it
        return Error, state

    translations = {
        'root' : [
            ('COMMENT', Comment),
            ('PATH', String),
            (('OPENBRACE', 'CLOSEBRACE'), Punctuation),
            (('SET', 'REPEAT', 'QUESTION'), Name.Keyword, 'args'),
            ('COMMAND', Name.Keyword, 'command_def'),
            ('LOAD', Name.Keyword),
            ('WORD', Name.Function, 'args'),
            ('NEWLINE', Whitespace),
            ('WHITESPACE', Whitespace),
        ],

        'args' : [
            ('COMMENT', Comment),
            ('OPERATOR', Operator),
            (('OPENPAREN', 'CLOSEPAREN'), Punctuation),
            (('OPENBRACE', 'CLOSEBRACE'), Punctuation),
            (('OPENBRACKET', 'CLOSEBRACKET'), String),
            ('NUMBER', Number),
            ('WORD', Name.Variable),
            ('NEWLINE', Whitespace, 'root'),
            ('WHITESPACE', Whitespace),
        ],

        'command_def' : [
            ('WORD', Name.Function, 'args'),
            ('WHITESPACE', Whitespace),
        ],
    }


class DBNStyle(Style):
    default_style = ""
    styles = {
        Text: "",
        Name.Keyword: "#00d bold",
        Name.Function: "#00d",
        Punctuation : "",
        Comment : "#66f italic",
        Name.Variable: "#090",
        String: "#f00",
        Number: "#a0a",
        Error: "bg:#f00 #eee"
    }

if __name__ == "__main__":
    import sys

    from pygments import highlight
    from pygments.formatters import Terminal256Formatter

    file_handle = open(sys.argv[1], 'r')
    code = file_handle.read()
    file_handle.close()

    print highlight(code, DBNLexer(), Terminal256Formatter(style=DBNStyle))
