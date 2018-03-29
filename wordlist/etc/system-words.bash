#! /usr/bin/env bash
set -e

pattern="$1"
# by default, skip all capitalized letters and contractions
[[ $pattern ]] || pattern="[=A-Z=]|[']"
DICT="$2"
[[ -f "$DICT" ]] || DICT=/usr/share/dict/words
[[ -f "$DICT" ]] || DICT="${0/*}/../lib/bips-0039-english-2048.txt"
[[ -f "$DICT" ]]

grep -vE "$pattern" "$DICT"
