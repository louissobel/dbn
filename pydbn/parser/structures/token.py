class DBNToken:
    """
    data encapsulation of a token
    """
    def __init__(self, type_, value, line_no, char_no, raw):
        """
        saves the given arguments as like-named attributes
        - type_ is value returned by the tokenizers classify method
        - value is the value of the token
        - line_no is the line on which the token appears
        - char_no is the character of that line
        - raw is the raw string that birthed this token
        """
        self.type = type_
        self.value = value

        self.line_no = line_no
        self.char_no = char_no

        self.raw = raw

    def get_end_char_no(self):
        return self.char_no + len(self.value)
    end_char_no = property(get_end_char_no)

    def __str__(self):
        return "%d:%d> %s %s" % (
            self.line_no,
            self.char_no,
            self.type,
            self.value,
        )