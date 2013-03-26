from base_adapter import BaseAdapter


class BasicImageRefresher(BaseAdapter):
    
    def __init__(self):
        self.new = False
    
    def identifiers(self):
        return ['image']
        
    def refresh(self):
        self.new = True
    
    def image(self):
        return self.interpreter().image._image
    
