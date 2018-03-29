#! /usr/bin/env bash

# Print a double-spaced screenful of random words, with some consideration about
# CPRNG (the included ushuf utility uses openssl).

# By default, only return words 3-8 letters long. This does not alter the Bitcoin
# BIPS-39 English list.

[[ $1 ]] && pattern="$1" || pattern='.\{3,8\}'

system-words.bash | grep -x "$pattern" | if [[ -t 1 ]]
then
  ushuf.bash -r -n 333 | column -x | sed G | head
else
  ushuf.bash -r
fi
