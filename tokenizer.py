import re



OPERATORS = r'[*-/+]'
GROUPERS = r'[\[\]{}\(\)]'
WORD = r'\w[\w\d]*'
NUMBER = r'\d+'
NEWLINE = r'\n'


ARGUMENT = '%s|%s|%s'

COMMENT = r'//.+%s' % NEWLINE


EVERYTHING_ELSE = r"\s+|."

TOKENS = r'(%s|%s|%s|%s|%s|%s|%s)' % (
    COMMENT,
    OPERATORS,
    GROUPERS,
    WORD,
    NUMBER,
    NEWLINE,
    EVERYTHING_ELSE,
)

class DBNToken:
    
    def __init__(self, token_match):
        #token
        pass

class DBNTokenizer:
    
    
    TOKENIZER_PATTERN = re.compile(TOKENS)
    
    def __init__(self):
        pass
        
        
    def tokenize(self, string):
        token_string_iter = self.TOKENIZER_PATTERN.finditer(string)
        for token_match in token_string_iter:
            token = DBNToken(token_match)
            print repr(token_match.group())
        
        
        
tokenizer = DBNTokenizer()

test_string = """
Line 0 5 60 (a+[0 3])
Repeat A 0 50
// foobee doobee woobe
{
    Paper (a * : 3 + 6 / 4) // some comment
    Pen 100
}
"""

tokenizer.tokenize(test_string)