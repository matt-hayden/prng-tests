#! /usr/bin/env python3
import os, os.path
from pathlib import Path
import subprocess

from .wordlist import WordListWithoutChecksum, WordListWithChecksum

PACKAGE_DIR = Path(__file__).parent
PACKAGE_ETC_DIR = PACKAGE_DIR / 'etc'
PACKAGE_LIB_DIR = PACKAGE_DIR / 'lib'
ENGLISH_2048 = PACKAGE_LIB_DIR / 'bips-0039-english-2048.txt'

system_words_execname = str(PACKAGE_ETC_DIR / 'system-words.bash')
proc = subprocess.run([system_words_execname], stdout=subprocess.PIPE)
if (0 == proc.returncode):
    ENGLISH = proc.stdout.decode().split()
else:
    ENGLISH = ENGLISH_2048
