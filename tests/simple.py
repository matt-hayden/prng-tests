#! /usr/bin/env python3
def info(text, *args):
    print(text % args)
debug = info

from wordlist import *

from codewords import *


lookup1 = WordListWithChecksum(codewords)
lookup2 = WordListWithoutChecksum(codewords)

def test1():
    c = lookup1.encode('correct')
    assert c == (1<<11)|388, c
    assert lookup1.encode('horse') == (1<<11)|878
    assert lookup1.encode('butter') == (0<<11)|250
    assert lookup1.encode('stamp') == (1<<11)|1699
def test2():
    assert 'correct' in lookup1.decode((1<<11)|388)
    assert 'horse' in lookup1.decode((1<<11)|878)
    assert 'butter' in lookup1.decode((0<<11)|250)
    assert 'stamp' in lookup1.decode((1<<11)|1699)
def test3():
    n = lookup1.encode('correct horse butter stamp')
    print(hex(n))
    assert ' '.join(lookup1.decode(n)) == 'correct horse butter stamp'
def test4():
    seq = lookup2.randomize(random.randrange(4, 12))
    print("Testing", seq)
    n = lookup1.encode(seq)
    for r, w in zip(range(12*len(seq), 1, -12), seq):
        try:
            bw = lookup1.decode(n^(1<<r))[i]
        except:
            print("Expected failure on %s... good" % (w))
        else:
            assert bw!=w, "Expected %s, got %s" % (w, bw)

if __name__ =='__main__':
    test1()
    test2()
    test3()
    test4()
