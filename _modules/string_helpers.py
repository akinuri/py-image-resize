def str_wrap(s, w = ""):
    return w + s + w

def str_quote(s):
    return str_wrap(s, "\"")

def str_repeat(s, count=1):
    return s * count

def tabspace(count=1):
    return str_repeat("    ", count)

def eol(count=1):
    return str_repeat("\n", count)

def str_pad_left(s, length, pad_char):
    s = str(s)
    str_len = len(s)
    if length > str_len:
        diff = length - str_len
        s = (pad_char * diff) + s
    return s

def str_pad_right(s, length, pad_char):
    s = str(s)
    str_len = len(s)
    if length > str_len:
        diff = length - str_len
        s += pad_char * diff
    return s

def filename(file_name):
    result = {
        "name"      : None,
        "extension" : None,
        "name_ext"  : file_name
    }
    if file_name == "." or file_name == "..":
        return result
    if "." in file_name:
        parts = file_name.split(".")
        result["extension"] = parts.pop().lower()
        result["name"]  = ".".join(parts)
    return result