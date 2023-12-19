import os

def resolveUi(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', filename))

def resolveImage(filename):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resources', filename))

def resolveData(filename):
    data = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))

    if not os.path.exists(data):
        os.makedirs(data)
        
    return os.path.abspath(os.path.join(data, filename))