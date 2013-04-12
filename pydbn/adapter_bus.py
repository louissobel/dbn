"""
A bus for things to attach between interpreter and external world
"""

class AdapterBus:
    
    def __init__(self):
        self._inner = {}
    
    def connect(self, interpreter):
        self.interpreter = interpreter
        return self
    
    def attach(self, adapter):
        identifier = adapter.identifier():
        self._inner[identifier] = adapter
        adapter.connect(self)
    
    def detach(self, identifier):
        del self._inner[identifier]
    
    def send(self, recipient, message, *args):
        recipient_adapter = self._inner.get(recipient)
        if recipient_adapter:
            method = getattr(recipient_adapter, message)
            if callable(method):
                return method(*args)
        return 0
                