import os

def keep_two_dirs(path):
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

path = "directory\\here.txt"
print("Path: " + path + ", Result: " + keep_two_dirs(path))

path = "\\some\\other\\directory\\here.txt"
print("Path: " + path + ", Result: " + keep_two_dirs(path))

path = "c:\\here.txt"
print("Path: " + path + ", Result: " + keep_two_dirs(path))

path = ".\\here.txt"
print("Path: " + path + ", Result: " + keep_two_dirs(path))

path = "here.txt"
print("Path: " + path + ", Result: " + keep_two_dirs(path))
