def test():
    print("''", "''", "'" + merge_text_strings("", "") + "'")
    print("''", "'aaaaa'", "'" + merge_text_strings("", "aaaaa") + "'")
    print("'aaaaa'", "''", "'" + merge_text_strings("aaaaa", "") + "'")
    print("'aaaaa'", "'aaaaa'", "'" + merge_text_strings("aaaaa", "aaaaa") + "'")
    print("'aabbbaaa'", "'bbb'", "'" + merge_text_strings("aabbbaaa", "bbb") + "'")
    print("'bbb'", "'aabbbaaa'", "'" + merge_text_strings("bbb", "aabbbaaa") + "'")
    print("'aaaaa'", "'bbbbb'", "'" + merge_text_strings("aaaaa", "bbbbb") + "'")


    #import json
    # print("Annotations 1: " + json.dumps(annotations1, indent=4))
    # print("Annotations 2: " + json.dumps(annotations2, indent=4))

