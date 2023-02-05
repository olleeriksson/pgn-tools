#!/usr/bin/python

import sys
from mod_pgn_subtree import pgn_subtree

try:
    filename = sys.argv[1]
    moves = sys.argv[2:]
except IndexError:
    raise SystemExit(f"Usage: {sys.argv[0]} <FILENAME> <MOVES...>")

pgn = pgn_subtree(filename, " ".join(moves))
print(pgn)
