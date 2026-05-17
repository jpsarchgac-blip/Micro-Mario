# urandom.py - MicroPython 'urandom' compatibility shim
from random import *  # noqa: F401, F403
import random as _r


def getrandbits(n):
    return _r.getrandbits(n)


def randrange(*a, **k):
    return _r.randrange(*a, **k)


def randint(*a, **k):
    return _r.randint(*a, **k)
