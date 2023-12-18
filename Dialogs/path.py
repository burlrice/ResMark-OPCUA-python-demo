import os

def resolveUi(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', filename))

def resolveImage(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', filename))