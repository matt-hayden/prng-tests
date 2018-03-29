#! /usr/bin/env python3
"""Correct Horse Battery Staple-style password generator

Usage:
  chbs [options] gen [--size=N] [ENCODING ...]
  chbs [options] expand <encoding> <word>
  chbs [options] encode <encoding> <words>...

  Where base64, base85 and hex are alternative encodings

Options:
  -b N --size=N             Size in bits
  -f FILE --wordlist=FILE   Location of specific word list
"""

import sys

from docopt import docopt

from . import *
from .util import *


def main():
    options = docopt(__doc__, version='0.1')
    wordlist = options.pop('--wordlist') or ENGLISH_2048
    def gen(numbits=float(options.pop('--size') or 64)):
        # When we randomly generate words, we use all bits
        wc = WordListWithoutChecksum(wordlist)
        numwords = wc.words_for_bits(numbits)
        return wc.randomize(numwords)
    def show(words, **kwargs):
        # When we encode and decode binary, we use bits with checksums
        print()
        wc = WordListWithChecksum(wordlist)
        print("For", wc)
        wc.show(words, **kwargs)
    if options['gen']:
        encodings = options.pop('ENCODING')
        words = gen()
        print(' '.join(words))
        if encodings:
            show(words, encodings=encodings)
    elif options['expand']:
        encoding = options.pop('<encoding>')
        word = options.pop('<word>')
        b = decoders[encoding](word)
        wc = WordListWithChecksum(wordlist)
        print(wc.decode(b))
    elif options['encode']:
        encoding = options.pop('<encoding>')
        assert encoding in encoders, "%s not found" % encoding
        words = options.pop('<words>')
        show(words, encodings=[encoding])
