# PGN Tools

A few python scripts to merge PGN files, extract sub-trees, and inject transpositions in a PGN file.

* [Merge PGN games/files into one](#merge-pgn)
* [Add transpositions to a PGN file](#transpositions)
* [Get a subtree from a PGN file](#pgn-subtree)


## Pre-requisites

These scripts require python to run, and that you also have [python-chess](https://python-chess.readthedocs.io)
installed.

```
pip install python-chess
```

<a name="merge-pgn"></a>
# Merge PGN games/files into one

Merge multiple PGN games into one with variations, from the same or multiple files. All games from all PGN files you pass to the script will be merged into one. Original version was based on [merge-pgn](https://github.com/permutationlock/merge-pgn) 

Usage
```
python merge-pgn.py  <PGN FILE 1> <PGN FILE 1>..  <OUTPUT FILE or - for STDOUT>
```

Example:
```
python merge-pgn.py  game1.pgn game2.pgn games3.pgn  -     (prints to STDOUT)
```

Example:
```
python merge-pgn.py  game1.pgn game2.pgn games3.pgn  all_games_merged.pgn
```

Or, one PGN with multiple games:
```
python merge-pgn.py  games.pgn  all_games_merged.pgn
```

## Comments

Merging of comments (including annotations like arrows and circles) are supported.

The following to PGN's:

```
1.e4 e5 { This is the first comment } {[%cal Gf2f5][%csl Gb3]}
```

```
1.e4 e5 { This is the second comment } {[%cal Ye2e3][%csl Yc4]}
```

..would be combined into this:

```
1.e4 e5 { This is the first comment

This is the second comment } { [%cal Gf2f5,Ye2e3][%csl Gb3,Yc4] }
```

Ie, normal text comments are merged and separated by two newlines. Identical comments are not duplicated.

### Caveats

One might argue that comments should be merged into completely separate {} sections. The PGN standard is vague on this, but most tools do it in this way. However because of a limitation in the [chess.pgn](https://github.com/niklasf/python-chess) library that this tool uses that was discussed [here](https://github.com/niklasf/python-chess/discussions/945) and [here](https://github.com/niklasf/python-chess/issues/946) only annotations ([%cal] and [%csl] etc) have been completely separated into separate {}'s, and even that in a kind of hacky solution.

<a name="transpositions"></a>
# Add transpositions to a PGN file

This script allows you to inject PGN subtrees into another PGN file where a transposition occurs, from within the same file or another file.

At the move where the transposition occurs, add a comment that looks like below. It's important that there are no other comments at all on this move, and no arrows or circles drawn. It has to be completely empty, apart from the following text:

```
Transposition: "<Any description>", <moves>, <transposition file>
```

The transposition file is the PGN file that has this exact sequence of moves somewhere inside it, and then however large a subtree of moves below it.

You can also leave the transposition file out if the transposed position exists in the current file, in which case it would look like this:

```
Transposition: "<Any description>", <moves>
```

Here are two examples:

```
Transposition: "Tennison Gambit", 1.e4 d5 2.Nf3, tennison.pgn
```
```
Transposition: "Tennison Gambit", 1.e4 d5 2.Nf3
```

The description is any number of words to describe the transposition. It helps to give them individual descriptions when some little detail is off and you're trying to find the problem. Also, the moves can be written with or without the move numbers, so just "e4 e5 Nf3" would work as well.

It's very important that you only add this comment in a location of the PGN file that represents the exact same position as the transposition you're describing. The move order can be different (obviously or it wouldn't be a transposition), but the position reached must be identical to the position you're referring to in the transposition comment. A check on the validity of the PGN tree is run so you will be informed if it's invalid, although this check does take some extra time.

## Basic example

Here is a basic example that uses only one file. example.pgn has a line that goes 1.e4 d5 2.Nf3 (which is the Tennison Gambit). This is followed by any number of moves and variations, but in this example it stops after 2 more moves. The Tennison Gambit can also be reached via 1.Nf3 d5 2.e4, resulting in the exact same position but via a different move order. So, we will include a transposition comment at the end of that second move order:

example.pgn:
```
1. e4 (1. Nf3 d5 2. e4 { Transposition: "Tennison Gambit", 1.e4 d5 2.Nf3 }) 1... d5 2. Nf3 { Tennison Gambit } 2... dxe4 3. Ng5 Nf6
```

The script is then called using these parameters:
```
python transpositions.py <input file> <output file> <transposition directory>
```



The transposition directory is the directory where the transposition files can be found. Since we are not pointing our transposition comments to a different file, we can leave this out. This can also be left out if the transposition files are in the same directory as the input file.

Last thing, instead of a filename you can write - (dash) to read from STDIN or write to STDOUT.

So, let's call the script like this:

```
python transpositions.py example.pgn -
```

And it will output the following to STDOUT.

```
1. e4 (1. Nf3 d5 2. e4 { Tennison Gambit } 2... dxe4 3. Ng5 Nf6) 1... d5 2. Nf3 { Tennison Gambit } 2... dxe4 3. Ng5 Nf6
```

As you can see the Tennison Gambit line is now duplicated at two different positions.

This simple example perhaps doesn't show the power of doing this since the transposition line is so short, but it if it was hundreds of moves in many different variations, they would be duplicated at both transposition points without having to enter every single move manually.

## Example with transposition lines in external files

Here is a practical example where the transposition lines are in an external file. The file main.pgn contains two transposition comments (at two different transpositions) pointing to the same position in the file tennison.pgn:

main.pgn:
```
1. e4 (1. Nf3 d5 2. e4 { Transposition: "Tennison Gambit", 1.e4 d5 2.Nf3, tennison.pgn }) 1... d5 2. exd5 (2. Nf3 { Transposition: "Tennison Gambit", 1.e4 d5 2.Nf3, tennison.pgn }) 2... Qxd5
```

tennison.pgn
```
1. e4 d5 2. Nf3 { Tennison Gambit } 2... dxe4 3. Ng5 Nf6
```

Ex:
```
python transpositions.py main.pgn output.pgn ./transpositions/
```

Output:

```
1. e4 (1. Nf3 d5 2. e4 { Tennison Gambit } 2... dxe4 3. Ng5 Nf6) 1... d5 2. exd5 (2. Nf3 { Tennison Gambit } 2... dxe4 3. Ng5 Nf6) 2... Qxd5
```

As you can see the Tennison Gambit lines (found in tennison.pgn) has been inserted at two different locations in main.pgn and then saved to output.pgn.


<a name="pgn-subtree"></a>
# Get a subtree from a PGN file

Returns the content or subtree at the specified location in a PGN game. The script currently only support PGN files with one single game so use merge-pgn.py above if you need to search for a specific line in multiple games.

Given a PGN game like this:
```
1. e4 { A comment } 1... e5 { Another comment } 2. Nf3 (2. Nc3 { [%cal Gg8f6,Gb8c6] } 2... Nf6 { A Nf6 comment } (2... Nc6 3. f4)) 2... Nc6 *
```

...calling this script with:
```
python pgn-subtree.py game.pgn 1.e4 e5 2.Nc3
```

...will return:
```
{ [%cal Gg8f6,Gb8c6] } 2... Nf6 { A Nf6 comment } ( 2... Nc6 3. f4 )
```

Ie, the whole subtree starting at 1.e4 e5 2.Nc3 will be returned including all comments from and including that move, excluding the move itself.



# Changelog

### 2023-03-12

- New flag to enable/disable following of transposition into other files.
- New flag to enable only printing a warning.

### 2023-02-27

- Using argparse for argument parsing.

### 2023-02-24

- New flag for transpositions.py to include a PGN validity check after transpositions are applied.
- New flag for merge-pgn.py to remove all comments.

### 2023-02-15

- transpositions.py can now run through the whole file and report all error afterwards instead of stopping at the first error.
- transpositions.py can now take global transposition files.

### 2023-02-12

- Added ability to save output to file with the last script argument or - for STDOUT.

### 2023-02-05

- Moved merge-pgn.py from the old repo to the new repo pgn-tools.
- Added transpositions.py.
- Added pgn-subtry.py.

### 2023-01-17

- Bugfix: Fixed a problem where multiple arrows of different colors were all kept. Now only the first encountered arrow in a specific location is kept.
- Feature: Headers that are identical in all games being merged are kept, and only those that are not common are left empty.

### 2023-01-08

- First modified version after forking https://github.com/permutationlock/merge-pgn.
