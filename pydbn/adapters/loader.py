"""
the loader adapter
"""
        
class LoadAdapter(object):
    
    def __init__(self, search_path=None):
        """
        save the search path, blah blah blah
        """
        pass
    
    def identifier(self):
        return 'loader'
    
    def load(self, file, offset):
        """
        returns the compiled bytecodes of the given file
        """
        print "load being called (%s, %d)" % (file, offset)
        return []