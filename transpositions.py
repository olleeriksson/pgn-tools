import sys
import os
import re
from mod_pgn_subtree import *
import argparse

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

def log_info(text, end="\n"):
    if args.output_file != "-":
        print(text, end=end, flush=True)

def log_debug(text, end="\n"):
    if args.output_file != "-" and args.verbose:
        print(text, end=end, flush=True)

def remove_lines_starting_with(str, skip_headers):
    skip_headers = ['[Event', '[Site', '[UTCDate', '[UTCTime', '[Variant', '[ECO', '[Opening', '[Result']
    lines = str.splitlines(keepends=True)
    new_lines = [n for n in lines if not n.startswith(tuple(skip_headers))]
    return "".join(new_lines)


#----------------------------------------------

class DefaultHelpParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

parser = DefaultHelpParser()
parser.add_argument('input_file', type=str, help="The input PGN file.")
parser.add_argument('output_file', type=str, help="The output PGN file.")
parser.add_argument('locations', type=str, nargs='*', help="One or more (space separated) PGN files or directories where transpositsions are searched in.")
parser.add_argument('--verbose', default=True, action=argparse.BooleanOptionalAction, help="Verbose output.")
parser.add_argument('--check', default=True, action=argparse.BooleanOptionalAction, help="Enables the verification of the validity of the PGN tree after applying the transpositions.")
parser.add_argument('--only-warn', default=False, action=argparse.BooleanOptionalAction, help="Print warnings instead of errors when unable to find a transposition.")
parser.add_argument('--follow-file', default=True, action=argparse.BooleanOptionalAction, help="Follows or doesn't follow the transposition file when looking for transpositions. Default is to follow the file.")
args = parser.parse_args()

if args.input_file == "-":
    pgn = "".join(sys.stdin.read())
else:
    f = open(args.input_file, encoding="utf-8")
    pgn = f.read()

# Remove certain headers
skip_headers = ['[Event', '[Site', '[UTCDate', '[UTCTime', '[Variant', '[ECO', '[Opening', '[Result']
pgn = remove_lines_starting_with(pgn, skip_headers)


error_label1 = ""             if args.only_warn else "\n"
error_label2 = "Warning"        if args.only_warn else "**** ERROR **** "
error_label3 = ""               if args.only_warn else "\n"

transposition_files = []
transposition_dirs = []
for location in args.locations:
    if os.path.isfile(location):
        transposition_files.append(location)
    elif os.path.isdir(location):
        if not location.endswith(os.path.sep):   # Add / or \ if it's not included
            location += os.path.sep
        transposition_dirs.append(location)
    else:
        log_info(f"Error. \"{location}\" doesn't exist.")
        exit()

# Add the input file as a transposition file
transposition_files.append(args.input_file)

# Add the directory of the input file as a transposition directory
input_file_dir = os.path.dirname(os.path.realpath(args.input_file)) + os.path.sep
if not input_file_dir in transposition_dirs:
    transposition_dirs.append(input_file_dir)

# Print all transposition files and dirs
log_debug(f"  Input file: \"{format_path(args.input_file)}\"")
log_debug(f"  Output file: \"{format_path(args.output_file)}\"")
log_debug(f"  Global transposition files and dirs:")
for file in transposition_files:
    log_debug(f"    File: \"{file}\"")
for dir in transposition_dirs:
    log_debug(f"    Dir:  \"{dir}\"")


# Looking for a comment like so:
#   Transposition: "Some text", bla bla moves bla bla[, filename.pgn]                       # filename is optional
#   Transposition: "Open Catalan", 1.d4 Nf6 2.c4 e6 3.g3 d5 4.Bg2 dxc4 5.Nf3, d4_catalan.pgn
#   Transposition: "Open Catalan", 1.d4 Nf6 2.c4 e6 3.g3 d5 4.Bg2 dxc4 5.Nf3
regex = re.compile(r'\{\s*Transposition:\s*\"(.*?)\",(.*?)(,(.*?))?\}', re.DOTALL)

match = regex.search(pgn)
num_matches = 0
num_errors = 0
while (match):
    info = match.group(1).strip()
    moves = match.group(2).strip()
    match_file = match.group(4).strip() if match.group(4) else ""

    first_non_space = pgn[match.end():].strip()[0]
    first_non_space_full = pgn[match.end():].strip()[0:40]

    replacement = ""

    if args.verbose:
        log_debug(f"\n  Transposition {num_matches + 1}:  [ {info} ]\n    Target moves:      {moves}     File: {format_path(match_file)}", "")
    else:
        log_info(".", "")

    # If a specific transposition file in the match is given, look for it in all transposition directories
    if match_file and args.follow_file:
        for dir in transposition_dirs:
            path = dir + match_file
            if os.path.isfile(path):
                replacement = pgn_subtree(path, moves)
                if replacement:
                    break
                #else:
                #    log_debug(f"\n      Not found in {format_path(path)} ... continuing", "")
    
    # Now look in the current file and transposition files provided by the caller of this script
    if not replacement:
        for file in transposition_files:
            replacement = pgn_subtree(file, moves)
            if replacement:
                break
            #else:
            #    log_debug(f"\n      Not found in {format_path(file)} ... continuing", "")

    # If a transposition file has not been found by now, give an error
    if not replacement:
        source = "any transposition file" if args.follow_file else "the current file"
        error_msg =  f"{error_label1}"
        error_msg += f"    {error_label2} {num_errors + 1}: Unable to find a move [{info}] with moves [{moves}] in {source}."
        error_msg += f"{error_label3}"
        if not args.only_warn or args.verbose:
            log_info(error_msg, "")
        replacement = "{ Transposition \"" + info + "\" to " + moves + " }"
        num_errors += 1

    elif first_non_space not in [")", "(", "*"]:
        error_msg =  f"{error_label1}"
        error_msg += f"    {error_label2} {num_errors + 1}: The move at transposition [{info}] with moves [{moves}] in {args.input_file} is not empty. \"{first_non_space_full}\""
        error_msg += f"{error_label3}"
        log_info(error_msg)
        replacement = "{ " + error_msg + " }"
        num_errors += 1

    # Double check to make sure the PGN is valid
    if args.check:
        try:
            test = pgn[:match.start()] + replacement + pgn[match.end():]
            pgn_subtree_from_string(test, moves)
        except AssertionError:
            print(f"")
            print(f"  **********************************************************")
            print(f"  * INVALID PGN")
            print(f"  * ERROR {num_errors + 1}: Applying move at transposition [{info}] with moves [{moves}] in {args.input_file} results in invalid PGN format.")
            print(f"  *    Make sure the move containing the transposition is not the first (main line) of several moves. Either make it the only move, or make sure it's not the first one (even if it happens to be the theoretical main line). This is a limitation of this program unfortunately.")
            print(f"  **********************************************************")
            print(f"")
            replacement = ""

    pgn = pgn[:match.start()] + replacement + pgn[match.end():]

    match = regex.search(pgn)
    num_matches += 1


look_for = "Transposition:"
remaining = pgn.count(look_for)
log_info(f"")
log_info(f"  ----------------------------------------------")
log_info(f"  Number of transpositions resolved: {num_matches - num_errors} / {num_matches}")
log_info(f"  *** WARNING! Number of remaining \"{look_for}\" occcurrancies: {remaining}") if remaining > 0 else ""
log_info(f"  ----------------------------------------------")

if args.output_file == "-" and num_errors == 0:
    print(pgn)
else:
    f = open(args.output_file, "w", encoding="utf-8")
    f.write(pgn)
    f.close()    

