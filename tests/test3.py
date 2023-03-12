import re
import sys

# Get the filename from the command line arguments
filename = sys.argv[1]

# Read the PGN file
with open(filename, 'r') as f:
    pgn = f.read()

def remove_lines_starting_with(str, skip_headers):
    lines = str.splitlines(keepends=True)
    new_lines = [n for n in lines if not n.startswith(tuple(skip_headers))]
    return "".join(new_lines)

skip_headers = ['[Event', '[Site', '[UTCDate', '[UTCTime', '[Variant', '[ECO', '[Opening', '[Result']
pgn = remove_lines_starting_with(pgn, skip_headers)

print(pgn)
