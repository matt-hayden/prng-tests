#! /usr/bin/env python3
import sys

from . import *


def main(verbose=False):
    execname, *args = sys.argv
    bits_s ,= args
    wc = WordListWithoutChecksum(ENGLISH_2048)
    r = wc.randomize(wc.words_for_bits(float(bits_s)))
    print(' '.join(r))
    n = WordListWithChecksum(ENGLISH_2048).encode(r)
    print(hex(n))
