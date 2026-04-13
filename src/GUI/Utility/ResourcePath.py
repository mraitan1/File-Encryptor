import sys, os

def resource_path(relative_path):
    # Returns absolute path
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(relative_path)
