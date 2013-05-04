from pygments.lexer import RegexLexer, bygroups
from pygments.token import *
from pygments.style import Style

class DBNLexer(RegexLexer):
    name = 'DBN',
    aliases= ['dbn']
    filenames = ['*.dbn']
    
    tokens = {
        'root' : [
            (r'[^\S\n]+', Text),
            (r'(Command)( )([A-z_][\w\d]*)', bygroups(Name.Keyword, Text, Name.Function), 'args'),
            (r'[A-z_][\w\d]*\??', Name.Keyword, 'args'),
            (r'\}', Punctuation),
            (r'//.+\n', Comment),
        ],
        
        'args' : [
            #(r'\[\s*\d+\s+\d+\s*\]', String),
            (r'\[', String),
            (r'\]', String),
            (r'[A-z_][\w\d]*', Name.Variable),
            (r'\d+', Literal.Integer),
            (r'[\(\)\{]', Punctuation),
            (r'[*/\-+]', Operator),
            (r'[^\S\n]+', Text),
            (r'\n', Text, '#pop'),
        ]
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
        Literal.Integer: "#a0a",
        Error: "bg:#f00 #eee"
    }
    
if __name__ == "__main__":
    import sys
    
    from pygments import highlight
    from pygments.formatters import TerminalFormatter, HtmlFormatter
    from pygments.styles import STYLE_MAP, get_style_by_name
    
    file_handle = open(sys.argv[1], 'r')
    code = file_handle.read()
    # for name in STYLE_MAP.keys():
    #     print "<h1>%s</h1>" % name
    #     print highlight(code, DBNLexer(), HtmlFormatter(noclasses=True, style=get_style_by_name(name)))
    
    print highlight(code, DBNLexer(), HtmlFormatter(noclasses=True, style=DBNStyle))
    