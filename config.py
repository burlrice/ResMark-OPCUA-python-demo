import json
import os

from Dialogs.path import resolveData

class Config:
    data = {}
    
    def __init__(self):
        try:
            with open(resolveData('settings.json'), "r") as json_file:
                self.data = json.load(json_file)
        except Exception as e:
            print(e)
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        with open(resolveData('settings.json'), "w") as json_file:
            json.dump(self.data, json_file, indent=4)
        
