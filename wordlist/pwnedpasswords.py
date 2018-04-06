#! /usr/bin/env python3
import binascii
import collections
import hashlib
import itertools
import os
from pathlib import Path
import shelve as kvs

import docopt
import requests


def find_database(paths=[Path(__file__).parent, '/var/cache/pwnedpasswords', '~/.cache/pwnedpasswords', '~/.cache', '~']):
    wd = None
    for d in paths:
        p = Path(d).expanduser()
        f = p / 'pwnedpasswords.db'
        if os.access(str(f), os.W_OK):
            return f
        elif not wd:
            if os.access(str(p), os.W_OK):
                wd = p
    if wd:
        return wd / 'pwnedpasswords.db'


def _make_key(data, hfunc=hashlib.sha1):
    key = data.encode() if isinstance(data, str) else data
    return hfunc(key).hexdigest().upper()

class PasswordHashCache:
    def __init__(self, filename=os.environ.get('CACHEFILE', None)):
        if not filename:
            filename = find_database() or '/tmp/pwnedpasswords.db'
        self.cache = kvs.open(str(filename))
        self.filename = filename
    def __enter__(self):
        return self
    def __exit__(self, e_type, e, traceback):
        # be sure to return True if any exception handling occurred
        self.cache.close()
    def update(self, hkeys):
        if not hkeys:
            return
        with requests.Session() as session:
            for page, _ in itertools.groupby(hkeys, lambda s: s[:5]):
                r = session.get('https://api.pwnedpasswords.com/range/'+page)
                assert r.ok, "Documentation says 404 shall never happen"
                self._update_page(page, r.text)
    def _update_page(self, prefix, text):
        for line in text.split('\n'):
            if not line:
                continue
            suffix, c = line.split(':')
            self.cache[(prefix+suffix).upper()] = int(c)
    def get_freqs(self, arg, refresh=False):
        """Get a Counter() with frequencies of passwords pwned

        Call with a dict in the form { hash: label } where label could be the cleartext, or maybe a username
        Call with any other iterable of strings, and those will be assumed to be passwords
        """
        if isinstance(arg, dict):
            lookup = arg
        else:
            lookup = { _make_key(k): k for k in arg }
        if refresh:
            notfound = list(lookup.keys()) # hash values
        else:
            notfound = [ hk for hk in lookup if hk not in self.cache ]
        if notfound:
            self.update(notfound)
        return collections.Counter( { lookup[hk]: self.cache.get(hk, 0) for hk in lookup } )

def get_freqs(*args, **kwargs):
    with PasswordHashCache() as c:
        return c.get_freqs(*args, **kwargs)
def check_password(arg, **kwargs):
    c = get_freqs([arg], **kwargs)
    return [ p for p, f in c.items() if not f ]
def check_hashes(values):
    c = get_freqs({ hk: n for n, hk in enumerate(values) }, **kwargs)
    return [ p for p, f in c.items() if not f ]

if __name__ == '__main__':
    if __debug__:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    import fileinput
    import sys

    lines = [ line.rstrip('\r\n') for line in fileinput.input() ]
    good = bad = 0
    for p, freq in get_freqs(lines).most_common():
        print("{: 18,d} {}".format(freq, p))
        if (freq == 0):
            good += 1
        else:
            bad += 1
    sys.exit(0 if good else 10)

