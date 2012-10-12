"""
A meta class for creating classes that return copies of themselves
when a mutating method is called
"""


class Immutable(type):
    
    def __init__(cls, name, bases, dict):
        type.__init__(cls, name, bases, dict)
        
        
        cls.a = 5
        
        
class TestImmutable:
    __metaclass__ = Immutable
    
    def foober(new):



if __name__ == "__main__":
    t = TestImmutable
    print type(t)
    print t.a