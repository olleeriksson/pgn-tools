import sys
import os
import re
from mod_pgn_subtree import pgn_subtree

def insert_braces(text):
    # Find all the occurrances of the braced string using re.finditer
    brace_matches = list(re.finditer(r'\{(.*?)\}', text, flags=re.DOTALL))

    # Iterate through all the matches (in reversed order because inserting stuff messes up the matches completely)
    for brace_match in reversed(brace_matches):
        start_pos = brace_match.start()
        end_pos = brace_match.end()

        # Find the position of the first [% within the braces
        percent_match = re.search(r'\[%', brace_match.group(1), flags=re.DOTALL)
        if percent_match is None:
            continue

        percent_pos = percent_match.start() + start_pos + 1

        comment_text = text[start_pos + 1:percent_pos].strip()

        # Insert "} {" at the position of the [% , if and only if the text before is non-empty
        if comment_text:
            text = text[:percent_pos] + "} { " + text[percent_pos:]

    return text

def format_path(path):
    last_sep = path.rfind(os.path.sep)
    if last_sep != -1:
        dir_path = path[:last_sep]
        second_last_sep = dir_path.rfind(os.path.sep)
        if second_last_sep != -1:
            return ".." + path[second_last_sep:]
        else:
            return path
    else:
        return path

def log_info(text):
    if output_file != "-":
        print(text)

#----------------------------------------------

try:
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    if len(sys.argv) == 4:
        dir = sys.argv[3]
    else:
        dir = ""
except IndexError:
    raise SystemExit(f"Usage: {sys.argv[0]} <INPUT_FILE> <OUTPUT_FILE> [<TRANSPOSITION_DIRECTORY>]")

if input_file == "-":
    pgn = "".join(sys.stdin.read())
else:
    # If the transposition dir has not been given, use the path of the input file
    if dir == "":
        dir = os.path.dirname(os.path.realpath(input_file)) + os.path.sep

    f = open(input_file, encoding="utf-8")
    pgn = f.read()
    

log_info(f"  Input file: \"{format_path(input_file)}\"")
log_info(f"  Output file: \"{format_path(output_file)}\"")
log_info(f"  Transposition dir: \"{format_path(dir)}\"")

# Looking for a comment like so:
#   Transposition: "Some text", bla bla moves bla bla[, filename.pgn]                       # filename is optional
#   Transposition: "Open Catalan", 1.d4 Nf6 2.c4 e6 3.g3 d5 4.Bg2 dxc4 5.Nf3, d4_catalan.pgn
#   Transposition: "Open Catalan", 1.d4 Nf6 2.c4 e6 3.g3 d5 4.Bg2 dxc4 5.Nf3
regex = re.compile(r'\{\s*Transposition:\s*\"(.*?)\",(.*?)(,(.*?))?\}', re.DOTALL)

match = regex.search(pgn)
num_matches = 0
while (match):
    info = match.group(1).strip()
    moves = match.group(2).strip()
    if match.group(4):
        transposition_file = dir + os.path.sep + match.group(4).strip()
    else:
        transposition_file = input_file

    log_info(f"  Transposition:  [{info}]\n    Target moves: [{moves}]\n    Target file:  {format_path(transposition_file)}")

    subtree = pgn_subtree(transposition_file, moves)

    first_non_space = pgn[match.end():].strip()[0]
    if first_non_space not in [")", "(", "*"]:
        print(f"  ERROR: The move at transposition [{info}] with moves [{moves}] in {input_file} is not empty. \"{first_non_space}\"")
        exit()

    if not subtree:
        print(f"  ERROR: Unable to find a move [{info}] with moves [{moves}] anywhere in transposition file {transposition_file}.")
        exit()

    #print("Found: " + str(match.start()) + " to " + str(match.end()) + "   group: [" + match.group(1) + "]")
    pgn = pgn[:match.start()] + subtree + pgn[match.end():]

    match = regex.search(pgn)
    num_matches += 1

log_info(f"  Number of transpositions: {num_matches}")

# Look for any remaining placeholders and report them as a way to catch any missed ones.
look_for = "Transposition:"
log_info(f"  Number of remaining \"{look_for}\" occcurrancies: {pgn.count(look_for)}")

if output_file == "-":
    print(pgn)
else:
    f = open(output_file, "w", encoding="utf-8")
    f.write(pgn)
    f.close()    
   
