import re

class DBNTokenClassifier:
    
    def __init__(self):
        self.pattern_list = []
        
    

OPERATORS = r'([*-/+])'

OPENPAREN = r'(\()'
OPENBRACKET = r'(\[)'
OPENBRACE = r'({)'
CLOSEPAREN = r'(\))'
CLOSEBRACKET = r'(\])'
CLOSEBRACE = r'(})'

GROUPERS = r'%s|%s|%s|%s|%s|%s' % (
    OPENPAREN,
    OPENBRACKET,
    OPENBRACE,
    CLOSEPAREN,
    CLOSEBRACKET,
    CLOSEBRACE,
)

SET = r'(Set)'
REPEAT = r'(Repeat)'
WORD = r'([A-z_][\w\d]*)'
NUMBER = r'(\d+)'
NEWLINE = r'\n'


COMMENT = r'//(.+)'


WHITESPACE = r"\s+"
EVERYTHING_ELSE = r"%s|." % WHITESPACE

# TODO clean this up
TOKENS = r'(%s|%s|%s|%s|%s|%s|%s|%s|%s)' % (
    COMMENT,
    OPERATORS,
    GROUPERS,
    SET,
    REPEAT,
    WORD,
    NUMBER,
    NEWLINE,
    EVERYTHING_ELSE,
)


class DBNToken:
    COMMENT_PATTERN = re.compile(COMMENT)
    OPERATOR_PATTERN = re.compile(OPERATORS)

    OPENPAREN_PATTERN = re.compile(OPENPAREN)
    OPENBRACKET_PATTERN = re.compile(OPENBRACKET)
    OPENBRACE_PATTERN = re.compile(OPENBRACE)
    CLOSEPAREN_PATTERN = re.compile(CLOSEPAREN)
    CLOSEBRACKET = re.compile(CLOSEBRACKET)
    CLOSEBRACE = re.compile(CLOSEBRACE)

    SET_PATTERN = re.compile(SET)
    REPEAT_PATTERN = re.compile(REPEAT)
    WORD_PATTERN = re.compile(WORD)
    NUMBER_PATTERN = re.compile(NUMBER)
    NEWLINE_PATTERN = re.compile(NEWLINE)
    WHITESPACE_PATTERN = re.compile(WHITESPACE)
    
    tokenizer_pattern_type = [
        (COMMENT_PATTERN, 'COMMENT'),
        (OPERATOR_PATTERN, 'OPERATOR'),

        (OPENPAREN_PATTERN, 'OPENPAREN'),
        (OPENBRACKET_PATTERN, 'OPENBRACKET'),
        (OPENBRACE_PATTERN, 'OPENBRACE'),
        (CLOSEPAREN_PATTERN, 'CLOSEPAREN'),
        (CLOSEBRACKET, 'CLOSEBRACKET'),
        (CLOSEBRACE, 'CLOSEBRACE'),

        (SET_PATTERN, 'SET'),
        (REPEAT_PATTERN, 'REPEAT'),
        (WORD_PATTERN, 'WORD'),
        (NUMBER_PATTERN, 'NUMBER'),
        (NEWLINE_PATTERN, 'NEWLINE'),
        (WHITESPACE_PATTERN, 'WHITESPACE')
    ]
    
    
    def __init__(self, token_match, line_no, char_no):
        """
        token_match is the MatchObject returned by the regex
        line_no is that line on which it occurs
        char_no is the
        """
        #token
        self.string = token_match.group(0)
        self.line_no = line_no
        self.char_no = char_no
        
        self.type = 'UNKNOWN'
        self.value = self.string
        self.tokenize()
        
    def tokenize(self):
        """
        sets the type of the token
        
        COMMENT
        OPERATOR *+/-

        OPENGROUP [({
        CLOSEGROUP })]
        
        WORD
        NUMBER
        NEWLINE
        
        WHITESPACE        
        """
        
        t = self.string
        for tokenizer_pattern, token_type in self.tokenizer_pattern_type:
            match = tokenizer_pattern.match(t)
            if match:
                self.type = token_type
                try:
                    self.value = match.group(1)
                except IndexError:
                    self.value = ''
                break

 
    def __str__(self):
         return "%d:%d> %s %s" % (self.line_no, self.char_no, self.type, self.value)
         

class DBNTokenizer:
    
    
    TOKENIZER_PATTERN = re.compile(TOKENS)
    
    def __init__(self):
        pass
        
        
    def tokenize(self, string):

        # for keeping track of where in the file we are
        line_no = 0
        line_start_char_no = 0
        
        token_string_iter = self.TOKENIZER_PATTERN.finditer(string)
        
        token_list = []
        for token_match in token_string_iter:
            token = DBNToken(token_match, line_no, token_match.start() - line_start_char_no)
            
            if token.type == 'COMMENT' or token.type == 'NEWLINE':
                line_no += 1
                line_start_char_no = token_match.end()
            
            if token.type == 'UNKNOWN':
                raise ValueError('unknown token at line %d char %d' % (token.line_no, token.char_no))
            
            
            if not token.type == 'WHITESPACE' and not token.type == 'COMMENT':
                token_list.append(token)
                
        return token_list
