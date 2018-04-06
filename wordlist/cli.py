"""Correct Horse Battery Staple-style password generator

Usage:
  chbs [options] gen [--size=N] [ENCODING ...]
  chbs [options] expand <encoding> <word>
  chbs [options] encode <encoding> <words>...

  Where base64, base85 and hex are alternative encodings

Options:
  -b N --size=N             Size in bits
  -f FILE --wordlist=FILE   Location of specific word list
  --pwnedpasswords          Check passwords against pwnedpasswords.com
  -d SEP --separator=SEP    Use this instead of space
"""
if __debug__:
    import logging
    logging.basicConfig(level=logging.DEBUG)

import sys

from docopt import docopt

from . import *
from .pwnedpasswords import check_password
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
        sep = options.pop('--separator') or ' '
        encodings = options.pop('ENCODING')
        words = gen()
        if options.pop('--pwnedpasswords'):
            while not all(check_password(pw) for pw in [ sep.join(words), ' '.join(words) ]):
                words = gen()
        print(sep.join(words))
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
