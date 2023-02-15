import re
import sys
import os

def extract_moves(pgn_string):
    # Compile a regular expression to match all SAN formatted chess moves
    pattern = re.compile(r'\b[KQRBN][a-h]?[1-8]?x?[a-h][1-8](=[QRBN])?[\+#]?\b')
    
    # Find all matches in the PGN string
    matches = pattern.finditer(pgn_string)
    
    # Extract and return the matched moves
    return [match.group(0) for match in matches]

def extract_event(pgn_string):
    # Compile a regular expression to match the "Event" field
    pattern = re.compile(r'\[Event "(.*)"\]')
    
    # Find the first match in the PGN string
    match = pattern.search(pgn_string)
    
    # Extract and return the event name
    return match.group(1) if match else ''

# Get the filename from the command line arguments
filename = sys.argv[1]

# Read the PGN file
with open(filename, 'r') as f:
    pgn_string = f.read()

# Split the PGN string into a list of games
games = pgn_string.split('\n[Event')

# Extract the moves and event name from each game and print the total number of moves
for game in games:
    game = '[Event' + game
    event = extract_event(game)
    moves = extract_moves(game)
    file = os.path.basename(filename)

    event_str = ""
    if (len(games) > 1):
        event_str = "    Event: " + event

    print(f'Number of moves: {len(moves):>5}   File: {file} {event_str}')

