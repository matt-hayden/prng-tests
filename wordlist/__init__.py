#! /usr/bin/env python3
import os, os.path
from pathlib import Path

from .wordlist import WordListWithoutChecksum, WordListWithChecksum

PACKAGE_DIR = Path(__file__).parent
ENGLISH_2048 = PACKAGE_DIR / 'bips-0039-english-2048.txt'
