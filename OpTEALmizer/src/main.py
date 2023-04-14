#!/bin/env python3
import os
import sys

if len(sys.argv) != 2:
    print(f"Usage python3 {sys.argv[0]} <filename>")
    sys.exit(1)

filename = sys.argv[1]

try:
    with open(os.path.join("src", filename)) as f:
        print(f.read())
except FileNotFoundError:
    # We don't have a hacked optimization so lets bail out
    with open(filename) as file:
        print(f.read())