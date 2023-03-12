import os
import sys

path = sys.argv[1]

if os.path.isfile(path):
    print("Is a file")

elif os.path.isdir(path):
    print("Is a directory")

else:
    print("None")
