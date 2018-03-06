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


def power_of_2_upper_bound(n, lo=0):
    i = lo
    while (1<<i) < n:
        i += 1
    return i
