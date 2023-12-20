from PyQt5.QtCore import Qt

class Busy:
   
    def __init__(self, widget):
        self.widget = widget
        self.cursor = widget.cursor()
        self.widget.setCursor(Qt.WaitCursor)             
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.widget.setCursor(self.cursor)
