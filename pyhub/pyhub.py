#!/usr/bin/env python
"""
    pip install virtualenv
    virtualenv --no-site-packages .
    python flow/pipgit.py flow/requirements.git > flow/requirements.pip
    source bin/activate
    pip install --no-dependencies -r flow/requirements.pip
    pip freeze > flow/requirements.txt

pyhub django/django @1.3.1
./src/
"""
import re
import sys
from github_repo import GitHubRepo

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


def write_to_file(path, content):
    f = open(path, 'w')
    f.write(content)
    f.close()

def command():
    c = Command()
    sources, reqs = c.requirements('requirements.github')
    print sources
    write_to_file('requirements.txt', sources+'\n')
    write_to_file('requirements.pip', reqs+'\n')


if __name__ == '__main__':
    command()
