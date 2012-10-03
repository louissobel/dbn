

class DBNBaseNode:
    pass
    
    
    
    
class DBNBlockNode(DBNBaseNode):
    
    
    def __init__(self):
        self.children = []
        
    def add_child(self, node):
        self.children.append(node)
        
    def __str__(self):
        return "(eval %s)" % ' '.join([str(c) for c in self.children])
        
    def pprint(self, depth=0, indent=4):
        print "%s(" % (' ' * depth * indent)
        for child in self.children:
            child.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
        

class DBNCommandNode(DBNBaseNode):
    
    def __init__(self, command_name, args):
        self.command_name = command_name
        self.args = args
        
    def add_arg(self, node):
        self.args.append(node)
        
    def __str__(self):
        return "(%s %s)" % (self.command_name, ' '.join([str(a) for a in self.args]))
        
    def pprint(self, depth=0, indent=4):
        print "%s(%s" % ((' ' * depth * indent), self.command_name)
        for arg in self.args:
            arg.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
        
        
class DBNBracketNode(DBNBaseNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    def __str__(self):
        return "(bracket %s %s)" % (str(self.left), str(self.right))
        
    def pprint(self, depth=0, indent=4):
        print "%s(bracket" % (' ' * depth * indent)
        self.left.pprint(depth=depth+1, indent=indent)
        self.right.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
        
        
class DBNBinaryOpNode(DBNBaseNode):
    def __init__(self, operation, left, right):
        self.operation = operation
        self.left = left
        self.right = right
        
    def __str__(self):
        return "(%s %s %s)" % (self.operation, str(self.left), str(self.right))
        
    def pprint(self, depth=0, indent=4):
        print "%s(%s" % ((' ' * depth * indent), self.operation)
        self.left.pprint(depth=depth+1, indent=indent)
        self.right.pprint(depth=depth+1, indent=indent)
        print "%s)" % (' ' * depth * indent)
                
class DBNNumberNode(DBNBaseNode):
    def __init__(self, numberstring):
        self.numberstring = numberstring
        
    def __str__(self):
        return "(%s)" % self.numberstring
    
    def pprint(self, depth=0, indent=4):
        print "%s%s" % ((' ' * depth * indent), str(self))
        
        
class DBNWordNode(DBNBaseNode):
    def __init__(self, wordstring):
        self.wordstring = wordstring
        
    def __str__(self):
        return "(%s)" % self.wordstring
        
    def pprint(self, depth=0, indent=4):
        print "%s%s" % ((' ' * depth * indent), str(self))