"""
Adapter base class
"""

class BaseAdapter(object):
    
    def connect(self, adapter_bus):
        self.adapter_bus = adapter_bus
    
    def interpreter(self):
        return self.adapter_bus.interpreter
    
    def identifers(self):
        raise NotImplementedError