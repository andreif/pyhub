#!/usr/bin/env python
"""
    pip install virtualenv
    virtualenv --no-site-packages .
    source bin/activate
    python pyhub.py
    pip install --no-dependencies -r requirements.local
"""
import re
import sys
from github_repo import GitHubRepo
from utils import write_file, append_file, read_file

class Command():
    def requirements(self, filename):
        sources = []
        source_file = open(filename, 'r')
        lines = source_file.read().split('\n')
        source_file.close()
        for line in lines:
            line = line.split('#')[0].strip()
            if len(line):
                print ' --> processing: %s' % line
                try:
                    m = re.search(r'(?P<user>\S+)/(?P<repo>\S+)(\s*@(?P<ref>\S+))?', line)
                    sources.append(GitHubRepo(user=m.group('user'), repo=m.group('repo'), ref=m.group('ref')))
                except Exception as e:
                    sys.stderr.write('Error for req "%s": %s\n' % (line, e))
        reqs = '\n'.join([s.req() or s.line() for s in sources])
        sources = '\n'.join([s.get_unpack_path() for s in sources])
        return sources, reqs


def command():
    c = Command()
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'requirements.github'
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'requirements.local'
    sources, reqs = c.requirements(input_file)
    print '-'*80
    print reqs
    print '-'*80
    print sources
    write_file(input_file + '.txt', reqs)
    write_file(output_file, sources)


if __name__ == '__main__':
    command()
