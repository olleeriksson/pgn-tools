import chess.pgn
import sys
import re
from io import StringIO
from collections import OrderedDict

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

def get_path(node):
    path = []
    path.append(node.san())
    cur_node = node.parent
    while cur_node.move:
        path.append(cur_node.san())
        cur_node = cur_node.parent
    nodes_ordered = reversed(path)
    return " ".join(nodes_ordered)

# Convert  "1.d4 Nf6 2.c4 e6"  to  "d4 Nf6 c4 e6"
# def strip_leading_move_number(move):
#     res = re.findall('^\s*\d*\.{0,3}\s*(\S*)\s*', move)
#     if res and res[0]:
#         return res[0]
#     else:
#         return move

# Convert  "1.d4 Nf6 2.c4 e6"  to  "d4 Nf6 c4 e6"
def normalize_and_strip_move_numbers(moves_str):
    res = re.sub('\d+\.{1,3}', '', moves_str)  # remove move numbers
    res = re.sub('\s{2,}', ' ', res)           # replace multiple whitespaces with one
    res = res.strip()
    return res

def strip_leading_move(text):
    regex = re.compile(r'\d+\.+\s*\S+\s*')
    match = regex.search(text)
    while (match):
        return text[match.end():]

def pgn_subtree(filename, moves_str):
    pgn_stream = open(filename, encoding="utf-8")
    return get_pgn_subtree(pgn_stream, moves_str)

def pgn_subtree_from_string(pgn_str, moves_str):
    pgn_stream = StringIO(pgn_str)
    sys.tracebacklimit = -1
    return get_pgn_subtree(pgn_stream, moves_str)

def get_pgn_subtree(pgn, moves_str):
    #moves = list(filter(None, moves_str.split(' ')))
    #print(f"Looking for moves: {moves}")

    #moves = map(lambda move: strip_leading_move_number(move), moves)
    #path = " ".join(moves)
    #print(f"  Without move numbers: {path}")

    path = normalize_and_strip_move_numbers(moves_str)
    #print(f"  Without move numbers: {path}")

    master_node = chess.pgn.Game()

    game = chess.pgn.read_game(pgn)

    mlist = []

    mlist.extend(game.variations)

    variations = [(master_node, mlist)]
    done = False

    while not done:
        newvars = []
        done = True
        for vnode, nodes in variations:
            newmoves = {}  # Maps move to its index in newvars.
            for node in nodes:
                #print(f"Move: {node.san()}  path: {get_path(node)}   comparing-to: {path}")
                if get_path(node) == path:
                    subtree = str(node)
                    
                    # Workaround to make sure the annotations end up in their own curly brackets,
                    # ie 1.e4 { A comment } { [%cal Ge2e4] }    instead of    1.e4 { A comment [%cal Ge2e4] }
                    pgn = insert_braces(subtree)
                    pgn = strip_leading_move(pgn)

                    return pgn

                if node.move is None:
                    continue
                elif node.move not in list(newmoves):
                    nvnode = vnode.add_variation(node.move, nags = node.nags)

                    if len(node.variations) > 0:
                        done = False
                    newvars.append((nvnode, node.variations))
                    newmoves[node.move] = len(newvars) - 1
                else:
                    nvnode, nlist = newvars[newmoves[node.move]]
                    nvnode.nags.update(node.nags)

                    if len(node.variations) > 0:
                        done = False
                    nlist.extend(node.variations)
                    newvars[newmoves[node.move]] = (nvnode, nlist)
        variations = newvars
    
    return ""

