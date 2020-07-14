import os


def collect(path=None, prefix=None):
    """
    Collect files from directory.
    """
    if not path:
        raise ValueError("No path is loaded.")
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if prefix and prefix in file:
                files.append(os.path.join(r, file))
    return files
