#! /usr/bin/env bash
# Utilize a slightly better source of randomness for shuf(1)

# Initialize AES128 with 16 random bytes.
function random_stream() {
  (head -c 16 /dev/urandom; cat /dev/zero) |
  openssl enc -aes128 -nosalt -pass file:/dev/urandom 2>/dev/null
}

shuf --random-source=<(random_stream) "$@"
