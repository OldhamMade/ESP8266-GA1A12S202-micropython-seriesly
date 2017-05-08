from gc import collect
from os import listdir


def conditionally_enable_webrepl():
    """Enable the webrepl if trigger file `webrepl_on` is found in the root."""
    if 'webrepl_on' in listdir():
        from webrepl import start
        start()
        collect()


def log_exception(e):
    """Capture log information to a file for later review."""
    with open('error.log', 'a') as f:
        f.write(str(e))
