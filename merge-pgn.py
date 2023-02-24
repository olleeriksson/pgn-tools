# Description: A simple tool to merge several pgn games into a single game with
# variations.

import chess.pgn
import sys
import re
from collections import OrderedDict
from itertools import filterfalse


# Extracts annotations from the comment
# cmd is for example %cal or %csl
# uci is e2e4
# color is G for green or B for blue
def extract_annotations(text):
    annotations = OrderedDict()
    normal_text = ""

    # Split the text by placeholders
    parts = re.split(r"\[|\]", text)
    for i, part in enumerate(parts):
        # Check if the current part is a placeholder
        if part and part[0] == "%":
            # Split the part by the white space
            cmd, values = part.split(" ", 1)
            # Split the values by the comma and strip any leading/trailing whitespace
            values = [value.strip() for value in values.split(",")]
            # Add the values to the annotations dictionary
            if cmd not in annotations:
                annotations[cmd] = OrderedDict()
            for value in values:
                uci = value[1:]
                color = value[0]
                annotations[cmd][uci] = color

        else:
            # Add the part to the normal_text variable
            normal_text += part

    # Replace multiple consecutive spaces with a single space in the normal_text variable
    normal_text = re.sub(r"\ ", " ", normal_text)

    return normal_text, annotations

def merge_text_strings(text1, text2):
    # If one is included in the other then it's a duplicate comment and should be ignored
    one_in_two = text1 and text2 and text1.casefold() in text2.casefold()
    two_in_one = text1 and text2 and text2.casefold() in text1.casefold()
    identical = one_in_two and two_in_one

    if identical:
        return text1
    if one_in_two:
        return text2
    if two_in_one:
        return text1
    if text1 and text2:
        transposition = "Transposition: "
        if transposition in text1 or transposition in text2:
            print(f"Found \"{transposition}\" in one of these two comments about to be merged:")
            print(f"Text1: \"{text1}\"")
            print(f"Text2: \"{text2}\"")
            sys.exit()
        return text1 + "\n\n" + text2
    if text1:
        return text1
    if text2:
        return text2
    return ""

# Picks one color of two according to a prio list when two colors are conflicting
def pick_color(color1, color2):
    color_prio = ['R', 'G', 'B', 'Y']    # highest prio first
    if color_prio.index(color1) < color_prio.index(color2):
        return color1
    else:
        return color2

def merge_annotations(annotations1, annotations2):
    for cmd2, ucis in annotations2.items():
        if cmd2 not in annotations1:
            annotations1[cmd2] = OrderedDict()
        for uci in ucis:
            ucis1 = annotations1[cmd2]

            if uci in ucis1:  # an arrow or circle of the same UCI and color (ie G and e2e4 in Ge2e4) already exist, use it!
                color1 = ucis1[uci]
                color2 = ucis[uci]
                ucis1[uci] = pick_color(color1, color2)
            else:
                color2 = ucis[uci]
                ucis1[uci] = color2

    # Format the merged annotations in the same way the placeholders appear in the text
    formatted_annotations = ""
    for cmd, ucis in annotations1.items():
        values = map(lambda uci: "" + ucis[uci] + uci, ucis)
        formatted_annotations += f"[{cmd} {','.join(values)}]"

    return formatted_annotations

def merge_comments(text1, text2):
    normal_text1, annotations1 = extract_annotations(text1)
    normal_text2, annotations2 = extract_annotations(text2)

    combined_text = merge_text_strings(normal_text1, normal_text2)
    combined_annotations = merge_annotations(annotations1, annotations2)

    return combined_text, combined_annotations

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

def main():
    usage = f"Usage: {sys.argv[0]} <PGN FILES>... <OUTPUT FILE> [--no-comments]\nWhere OUTPUT_FILE can be - to indicate STDOUT."

    if len(sys.argv) <= 2:
        raise SystemExit(usage)
    try:
        filter_options = lambda x: re.match("^--[a-zA-Z-]*", x)
        options = list(filter(filter_options, sys.argv))
        sys.argv = list(filterfalse(filter_options, sys.argv))

        infiles = sys.argv[1:-1]
        outfile = sys.argv[-1]
    except IndexError:
        raise SystemExit(usage)

    master_node = chess.pgn.Game()

    games = []
    for name in infiles:
        pgn = open(name, encoding="utf-8")
        game = chess.pgn.read_game(pgn)
        while game is not None:
            text, annotations = merge_comments(master_node.comment, game.comment)

            if "--no-comments" in options and not "Transposition:" in text:
                text = ""

            master_node.comment = f"{text}{annotations}"

            games.append(game)
            game = chess.pgn.read_game(pgn)

    mlist = []
    headers = {}
    for game in games:
        mlist.extend(game.variations)

        # Save all headers from all games
        for header in game.headers.keys():
            if header not in headers:
                headers[header] = set()
            headers[header].add(game.headers[header])

    # Set those headers that had common values in all games
    for header in headers:
        values = headers[header]
        if len(values) == 1:
            value = values.pop()
            master_node.headers[header] = value

    variations = [(master_node, mlist)]
    done = False

    while not done:
        newvars = []
        done = True
        for vnode, nodes in variations:
            newmoves = {}  # Maps move to its index in newvars.
            for node in nodes:
                if node.move is None:
                    continue
                elif node.move not in list(newmoves):
                    nvnode = vnode.add_variation(node.move, nags = node.nags)
                    text, annotations = merge_comments(node.comment, "")

                    if "--no-comments" in options and not "Transposition:" in text:
                        text = ""

                    nvnode.comment = f"{text}{annotations}"

                    if len(node.variations) > 0:
                        done = False
                    newvars.append((nvnode, node.variations))
                    newmoves[node.move] = len(newvars) - 1
                else:
                    nvnode, nlist = newvars[newmoves[node.move]]
                    text, annotations = merge_comments(nvnode.comment, node.comment)
                    nvnode.comment = f"{text}{annotations}"
                    nvnode.nags.update(node.nags)

                    if len(node.variations) > 0:
                        done = False
                    nlist.extend(node.variations)
                    newvars[newmoves[node.move]] = (nvnode, nlist)
        variations = newvars

    pgn = f"{master_node}"

    # Workaround to make sure the annotations end up in their own curly brackets,
    # ie 1.e4 { A comment } { [%cal Ge2e4] }    instead of    1.e4 { A comment [%cal Ge2e4] }
    pgn = insert_braces(pgn)
    
    if outfile == "-":
        print(pgn)
    else:
        f = open(outfile, "w", encoding="utf-8")
        f.write(pgn)
        f.close()

main()
