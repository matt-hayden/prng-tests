#! /usr/bin/env python3
"""A module for checking passwords against a big online list.

Prints the number of times your input passwords have appeared on the Dark
Web. Yes, really.

Enter the passwords you'd like to check in stdin, or list their filenames as
command-line arguments. Those passwords are _never_ transmitted or stored in
the clear -- they're hashed using SHA-1. If using stdin, type your passwords,
then end with Ctrl-D on Linux, or Ctrl-Z on Windows.

For well-formatted introspection:

$ python3
Python 3.5.2 (default, Nov 23 2017, 16:37:01) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import pwnedpasswords
>>> help(pwnedpasswords)


 ___________________________________________________________________________
/ yes, if you've paid attention in class, cryptographers consider SHA-1 too \\
\ weak for future sensitive use.                                            /
 ---------------------------------------------------------------------------
        \\
         \\
           ((((
           {  '>
           / ,\\
     jgs  /_/ /
       ===//="======
         /
"""

# Built-in libraries
import binascii             # Convenience functions for ascii<->binary representations
import collections          # Specialized lists, arrays, and dict()s
import hashlib              # General hashing functions
import itertools            # Manipulations on functions that yield, rather than return
import os                   # Operating system specific routines, like opening files
from pathlib import Path    # An overly-complicated way to use paths (aren't strings good enough?)
import shelve as kvs        # A key-value store. I don't care which one, but 'shelve' is built-in

# Third-party libraries
import requests             # HTTP client


# __file__ is a special variable. The underscores are mandatory. It's a string
# holding the path of this file. From system to system, that path will be
# different.
module_dir = Path(__file__).parent


def find_database(paths=[ module_dir,
                         '/var/cache/pwnedpasswords',
                         '~/.cache/pwnedpasswords',
                         '~/.cache',
                         '~' ]):
    wd = None # This variable could have been named some_writable_directory,
              # I suppose, but my underscore key is way  over  there.
    for d in paths:
        p = Path(d).expanduser()
        f = p / 'pwnedpasswords.db'
        # The os.access function (and others like it) take a flag as a second
        # parameter. That flag always has a capitalized name, and os.W_OK is the
        # flag for check-if-this-is-writable.
        if os.access(str(f), os.W_OK):
            return f
        elif not wd:
            if os.access(str(p), os.W_OK):
                wd = p
    if wd: # If we got here, we did not return in the above loop.
        return wd / 'pwnedpasswords.db'
    # We reached the end of the function without returning. A 'return None' is
    # implied.


# This function starts with an underscore. That convention tells Python not to
# make this function importable. It's still visible / introspection-able, but I
# don't intend for its behaviour to be stable if I have to make any future
# improvements.
def _make_key(data, hfunc=hashlib.sha1):
    # The hfunc argument is for a function. Functions are first-class objects,
    # and can be passed around _as well as_ called with arguments.
    
    # strings in Python 3 are Unicode-aware. By contrast, arrays of bytes, each
    # precisely 8 bits, are not equivalent to strings. This line demonstrates
    # a variable that always holds an array of bytes. If data is a string, it's
    # passed the .encode() method, which converts it into bytes:
    key = data.encode() if isinstance(data, str) else data
    # I treat this function in a very specific way. Not many functions will
    # behave as I intend here:
    return hfunc(key).hexdigest().upper()


class PasswordHashCache:
    """A persistent local cache for password lookups.
    """
    # somelookup.get(key) is a function that performs a lookup like
    # somelookup[key]. Optionally, you can give a default value if key is not
    # found. somelookup.get(key, 'greaseball') will thusly return 'greaseball'
    # rather than erroring out.
    def __init__(self, filename=os.environ.get('CACHEFILE', None)):
        """The file used for the local cache is decided in this order:
            * The environment variable $CACHEFILE
            * The system-wide /var/cache/pwnedpasswords/pwnedpasswords.db
            * The user's ~/.cache/pwnedpasswords/pwnedpasswords.db
            * The user's ~/.cache/pwnedpasswords.db
            * Temporary /tmp/pwnedpasswords.db
        """
        if not filename:
            filename = find_database() or '/tmp/pwnedpasswords.db'
        self.cache = kvs.open(str(filename))
        self.filename = filename
    def __enter__(self):
        # An __enter__ method allows this class to handle statements like:
        #   with PasswordHashCache() as my_very_own_cache:
        #       I.run.my.very.own.code
        #   my_very_own_cache leaves scope before this line
        return self
    def __exit__(self, e_type, e, traceback):
        # This must be defined alongside __enter__
        # be sure to return True if any exception handling occurred
        self.cache.close()
    def update(self, hkeys):
        """Check an iterable of _hashed_ passwords against the web
        site pwnedpasswords.com.
        """
        if not hkeys:
            return
        hkeys.sort()
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
            # This construct forms a dict() object in one step. Keys and values
            # are paired with : in between. This dict() looks up things that
            # the 
            lookup = { _make_key(k): k for k in arg }
        if refresh:
            notfound = list(lookup.keys()) # .keys() generates a series,
                                           # not an array, so I have to wrap
                                           # it in a list() constructor.
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
    # These lines are only executed if this script was run from the command
    # line. For example, if in bash, you `python3 pwnedpasswords.py myfile`,
    # then expect this to be executed. If in python, you `import
    # pwnpasswords.py`, then only the functions above are respected.
    if __debug__:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Some more imports, not used above, so not necessary to lump in with the
    # section at the top of the file.
    import fileinput    # Convenient way to loop over input files
    import sys          # Platform dependent artifacts

    # This is a common pattern to digest the output of fileinput.input(), which
    # is a generator for individual lines, take any carriage return (\r) and
    # line feed (\n) off the right side of the string, and shove those into a
    # list.
    lines = [ line.rstrip('\r\n') for line in fileinput.input() ]
    good = bad = 0 # This pattern is only useful for primitive objects.
                   # You don't want to do this with class instances.
    # get_freqs returns a list of pairs of values, so my for loop can
    # `dereference` those pairs with a comma:
    for p, freq in get_freqs(lines).most_common():
        # Python has the % string substitution operator, but it also has the
        # bracket string template syntax. It's slower, but more powerful. For
        # example, this syntax prints the freq variable, padded with spaces to
        # exactly 18 characters wide, with commas separating thousands, etc.
        # That's not possible with a % substitution.
        print("{: 18,d} {}".format(freq, p))
        if (freq == 0):
            good += 1
        else:
            bad += 1
    # sys.exit() sets the returncode. This is useful on the command line -- it
    # silently passes a success or failure integer to the next program. But,
    # importantly, the logic is opposite boolean: 0 is success, anything
    # nonzero is failure. So, if good is truthy, I exit 0 (success), if good is
    # falsey, I exit 10 (one of many failure codes). Conventionally, you can
    # use codes 3-63.
    sys.exit(0 if good else 10)

