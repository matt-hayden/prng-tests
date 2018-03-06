#! /usr/bin/env python3
import logging
logger = logging.getLogger(__name__)
debug, info, warn, error, panic = logger.debug, logging.info, logging.warn, logging.error, logging.critical

import bisect
import math
from pathlib import Path

from .util import *


class WordListBase:
    def __init__(self, iterable):
        if isinstance(iterable, (str, Path)):
            filename = Path(iterable)
            iterable = [ line.strip() for line in filename.open('Ur') ]
        self.values = list(iterable)
        info("wordlist is len(%d)", len(self.values))
        wl = self.wordlength = power_of_2_upper_bound(len(self.values))
        self.wordmask = (1<<wl)-1
        debug("wordlength %d, wordmask 0x%x", self.wordlength, self.wordmask)
    def words_for_bits(self, nbits):
        return math.ceil( nbits/math.log2(len(self.values)) )
    def lookup(self, value):
        i = bisect.bisect_left(self.values, value)
        assert self.values[i] == value
        return i
    def encode(self, words, prefix=0):
        if isinstance(words, str):
            words = words.split()
        b = prefix
        for w in words:
            b <<= self.wordlength
            b |= self.lookup(w)
        return b
    def _decode_r(self, number):
        while number:
            i = number&self.wordmask
            yield self.values[i]
            number >>= self.wordlength
    def decode(self, *args):
        rvalues = list(self._decode_r(*args))
        rvalues.reverse()
        return rvalues
    def randomize(self, length):
        return [ choice(self.values) for _ in range(length) ]
class WordListWithoutChecksum(WordListBase):
    """
    Without a checksum, integer 0 does not generate distinct passphrases.

    For example:
        ['ability'] -> 0
        ['ability']*X -> 0
    """
class WordListWithChecksum(WordListBase):
    """
    This checksum is the length of the word mod 2.

    For example:
        checksum('ability') -> 1
        encode(['ability']) -> 0b100,000,000,001
    """
    def __init__(self, iterable, checksum=None):
        super().__init__(iterable)
        self.checkmask = (1<<self.wordlength)
        self.wordlength += 1
        debug("new wordlength %d, wordmask 0x%x, checkmask 0x%x", self.wordlength, self.wordmask, self.checkmask)
        if not checksum:
            def checksum(w):
                return len(w) % 2
        assert checksum(self.values[0]), \
               "Poorly designed checksum function should be nonzero for zeroth value"
        self.checksum = checksum # staticmethod
    def encode(self, words):
        if isinstance(words, str):
            words = words.split()
        b = 0
        for w in words:
            b <<= self.wordlength
            b |= (self.checkmask*self.checksum(w))|self.lookup(w)
        return b
    def _decode_r(self, number):
        while number:
            i = number&self.wordmask
            check_bit = 1 if (number&self.checkmask) else 0
            w = self.values[i]
            assert self.checksum(w) == check_bit, "Checksum failed on '%s'" % w
            yield w
            number >>= self.wordlength
