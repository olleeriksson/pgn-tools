def merge_text_strings(text1, text2):
    lookfor = "Harwitz Attack / Blackburn Variation"
    if lookfor in text1 or lookfor in text2:
        print("Text1: \"" + text1 + "\"")
        print("Text2: \"" + text1 + "\"")

    # If one is included in the other then it's a duplicate comment and should be ignored
    one_in_two = text1 and text2 and text1.casefold() in text2.casefold()
    two_in_one = text1 and text2 and text2.casefold() in text1.casefold()
    identical = one_in_two and two_in_one

    if identical:
        if lookfor in text1 or lookfor in text2:
            print("Identical")
            print("")
        return text1
    if one_in_two:
        if lookfor in text1 or lookfor in text2:
            print("use 2")
            print("")
        return text2
    if two_in_one:
        if lookfor in text1 or lookfor in text2:
            print("use 1")
            print("")
        return text1
    if text1 and text2:
        if lookfor in text1 or lookfor in text2:
            print("merge")
            print("")
        return text1 + "\n\n" + text2
    if text1:
        if lookfor in text1 or lookfor in text2:
            print("1")
            print("")
        return text1
    if text2:
        if lookfor in text1 or lookfor in text2:
            print("2")
            print("")
        return text2
    return ""


def print_compare_strings(text1, text2):
    print(f"'{text1}', '{text2}' --> '{merge_text_strings(text1, text2)}'")

def test():
    print_compare_strings("", "")
    print_compare_strings("", "aaaaa")
    print_compare_strings("aaaaa", "")
    print_compare_strings("aaaaa", "aaaaa")
    print_compare_strings("aabbbaaa", "bbb")
    print_compare_strings("bbb", "aabbbaaa")
    print_compare_strings("aaaaa", "bbbbb")
    print_compare_strings("aaaaa", "bbbbb")
    
    text1 = "Transposition: \"1.d4 d5 2.c4 e6 3.Nc3 Be7 4.Bf4 Nf6 5.e6 O-O 6.Nf3 - Alatortsev Variation to the Harwitz Attack / Blackburn Variation 1 move deeper\", 1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Nf3 Be7 5.Bf4 O-O 6.e3"
    text2 = "Transposition: \"1.d4 d5 2.c4 e6 3.Nc3 Be7 4.Bf4 Nf6 5.e6 O-O 6.Nf3 - Alatortsev Variation to the Harwitz Attack / Blackburn Variation 1 move deeper\", 1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Nf3 Be7 5.Bf4 O-O 6.e3"
    print_compare_strings(text1, text2)

    filecontent1 = open("d4_QG_albin1.pgn", encoding="utf-8").read()
    filecontent2 = open("d4_QG_albin2.pgn", encoding="utf-8").read()
    print_compare_strings(filecontent1, filecontent2)

    #import json
    # print("Annotations 1: " + json.dumps(annotations1, indent=4))
    # print("Annotations 2: " + json.dumps(annotations2, indent=4))

test()
