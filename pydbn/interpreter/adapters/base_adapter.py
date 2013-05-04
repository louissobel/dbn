"""
Adapter base class
"""

class BaseAdapter(object):
    
    def connect(self, adapter_bus):
        self.adapter_bus = adapter_bus

    def interpreter(self):
        return self.adapter_bus.interpreter
    
    def identifier(self):
        raise NotImplementedError

    def debug(self, message):
        """
        tries to debug or noop
        """
        try:
            self.interpreter().debug(message)
        except AttributeError:
            pass
