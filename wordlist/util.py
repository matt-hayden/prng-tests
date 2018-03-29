#! /usr/bin/env python3
"""
Python 3.6 has a new crypto built-in package called secrets.
"""
try:
    import secrets
    choice = secrets.choice
except ImportError:
    import random
    choice = random.SystemRandom().choice

import base64
import binascii

def rawhex(text):
    """
    Returns even-length hex strings without 0x at the beginning
    """
    if text.startswith('0x'):
        text = text[2:]
    if (len(text) % 2):
        text = '0'+text
    return text
def unhexlify(arg, **kwargs):
    return binascii.unhexlify(rawhex(arg))
def b64t(arg, b64encode=base64.b64encode):
    "hex to base-64"
    return b64encode(unhexlify(arg))
def b64n(arg, b64decode=base64.b64decode):
    "base-64 encoded text to integer"
    i = 0
    for b in b64decode(arg):
        i <<= 8
        i |= b
    return i
def b85t(arg, b85encode=base64.b85encode):
    "hex to base-85"
    return b85encode(unhexlify(arg))
def b85n(arg, b85decode=base64.b85decode):
    "base-85 encoded text to integer"
    i = 0
    for b in b85decode(arg):
        i <<= 8
        i |= b
    return i

decoders = { 'hex':     lambda i: i, \
             'base64':  lambda i: b64n(i), \
             'base85':  lambda i: b85n(i) }
encoders = { 'hex':     lambda i: i, \
             'base64':  lambda i: b64t(i).decode(), \
             'base85':  lambda i: b85t(i).decode() }

def power_of_2_upper_bound(n, lo=0):
    i = lo
    while (1<<i) < n:
        i += 1
    return i
