## Function to turn a pydbn astnode into a dbn.js one
## Sweeet

def pydbn2dbnjs(self, depth=0, varname=None):
    """
    we use a two space indent, by the way
    """
    header_lines = [
        "new DBNASTNode({",
        "  type: '%s'," % self.type,
        "  name: '%s'," % self.name,
        "  tokens: [],",
        "  lineNo: %d," % self.line_no,
        "  children: [%s" % ('\n' if self.children else ']'),
    ]
    
    out = '\n'.join([depth  * "  " + l for l in header_lines])
    child_js = [pydbn2dbnjs(child, depth+2) for child in self.children]
    out += ',\n'.join(child_js) + '\n'
    
    if self.children:
        footer_lines = [ "  ]" ]
    else:
        footer_lines = []
    
    footer_lines.append("})")
    
    out += '\n'.join([depth  * "  " + l for l in footer_lines])
    
    if varname is not None:
        out = "var %s = %s" % (varname, out)
    
    return out