
def read_file(path):
    f = open(path, 'r')
    contents = f.read()
    f.close()
    return contents

def write_file(path, contents):
    f = open(path, 'w')
    i = f.write(contents)
    f.close()
    return i
