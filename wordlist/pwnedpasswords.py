#! /usr/bin/env python3
import binascii
import collections
import hashlib
import itertools
import os
from pathlib import Path
import shelve as kvs

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
    def get_hash_freqs(self, hkeys, refresh=False):
        hkeys = list(hkeys)
        if refresh:
            notfound = hkeys
        else:
            notfound = [ hk for hk in hkeys if hk not in self.cache ]
        if notfound:
            self.update(notfound)
        return collections.Counter( { hk: self.cache.get(hk, 0) for hk in hkeys } )
    def get_freqs(self, keys, hfunc=hashlib.sha1):
        lookup = { _make_key(k): k for k in keys }
        c = collections.Counter()
        for hk, freq in self.get_hash_freqs(lookup.keys()).items():
            c[lookup.pop(hk)] = freq
        assert not lookup
        return c
def get_freqs(keys):
    with PasswordHashCache() as c:
        return c.get_freqs(keys)
def check_password(*args):
    c = get_freqs(*args)
    return [ p for p, f in c.items() if not f ]

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    import fileinput

    lines = [ line.rstrip('\r\n') for line in fileinput.input() ]
    for p, freq in get_freqs(lines).most_common():
        print("{: 18,d} {}".format(freq, p))

