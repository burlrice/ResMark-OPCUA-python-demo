import os

from PyQt5.QtWidgets import QWidget

def resolveUi(filename: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', filename))

def resolveImage(filename: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', filename))

def resolveData(filename: str) -> str:
    data = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

    if not os.path.exists(data):
        os.makedirs(data)
        
    return os.path.abspath(os.path.join(data, filename))

def resolveTopMostWidget(widget) -> QWidget:
    while widget.parent():
        widget = widget.parent()
        
    return widget

def resolveMessage(message: str) -> str:
    return message if message.endswith('.next') else f'{message}.next'