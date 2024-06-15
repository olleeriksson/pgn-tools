import sys
import os

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from mod_pgn_subtree import *

def print_before_and_after(move):
    print(f"\"{move.ljust(18)}\" -> \"{normalize_and_strip_move_numbers(move)}\"")

print_before_and_after("3.d4")
print_before_and_after("10. d4")
print_before_and_after(".d4")
print_before_and_after("d4")
print_before_and_after(" 1.d4")
print_before_and_after("  1.  d4")
print_before_and_after("  d4 ")
print_before_and_after("1..d4")
print_before_and_after("1... d4")
print_before_and_after("10..d4")
print_before_and_after("   1...   d4 ")
print_before_and_after("1..Nf6")
print_before_and_after("   1...   Nf6 ")
print_before_and_after("4.O-O")
print_before_and_after("   4.   O-O ")
print_before_and_after("1..O-O")
print_before_and_after("   1...   O-O ")
print_before_and_after("4.O-O-O")
print_before_and_after("   4.   O-O-O ")
print_before_and_after("   O-O-O ")
print_before_and_after("5..O-O-O")
print_before_and_after("   1...   O-O-O ")
print_before_and_after("1..exd4")
print_before_and_after("   1...   exd4 ")




print("\"" + strip_leading_move("1.e4 { Some comment } {[%cal Ge2e4]}") + "\"")


