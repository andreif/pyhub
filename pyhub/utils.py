
def read_file(path, default=''):
    try:
        f = open(path, 'r')
        contents = f.read()
        f.close()
        return contents
    except IOError as e:
        return default

def write_file(path, contents):
    f = open(path, 'w')
    i = f.write(contents)
    f.close()
    return i

def append_file(path, contents):
    f = open(path, 'a')
    i = f.write(contents)
    f.close()
    return i
