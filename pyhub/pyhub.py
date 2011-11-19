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

import os
import re
import sys

from github_api_v3 import GitHubAPI

class GitHubRepo():
    
    def __init__(self, user, repo, ref=None):
        self.github = GitHubAPI(user=user, repo=repo, ref=ref)
        self.path = './src'
        self.download_and_unpack()

    def download_and_unpack(self):
        if self.downloaded(): return
        if not os.path.exists(self.path): os.makedirs(self.path)
        self.remove_old_versions()
        os.system('curl %s | tar xz --directory=%s' % (
            self.github.get_tarball_url(),
            self.path
        ))
        os.system('mv %s/%s-%s-* %s' % (self.path, self.github.user, self.github.repo, self.get_unpack_path()))
        if not self.downloaded():
            raise Exception('Failed to download github repo "%s" for sha %s' % (self.github.repo, self.github.short_sha()))

    def downloaded(self):
        return os.path.exists(self.get_unpack_path())

    def remove_old_versions(self):
        os.system('rm -r %s/%s-%s-*' % (self.path, self.github.user, self.github.repo))

    def get_unpack_path(self):
        return '%s/%s-%s-%s' % (
            self.path,
            self.github.user,
            self.github.repo,
            self.github.short_sha(),
        )

    def line(self):
        return '-e ' + self.get_unpack_path()

    def req(self):
        return '-e git+git@github.com:%s/%s.git@%s#egg=%s-dev' % (
            self.github.user,
            self.github.repo,
            self.github.commit_sha,
            self.github.repo
        )


class Command():
    def requirements(self, filename):
        source_file = open(filename)
        sources = []
        lines = source_file.read().split('\n')
        for line in lines:
            line = line.split('#')[0].strip()
            if len(line):
                try:
                    m = re.search(r'(?P<user>\S+)/(?P<repo>\S+)(\s*@(?P<ref>\S+))?', line)
                    repo = GitHubRepo(user=m.group('user'), repo=m.group('repo'), ref=m.group('ref'))
                    sources.append(repo)
                    
                except Exception as e:
                    sys.stderr.write('%s %s' % (line, e))
        reqs = '\n'.join([s.req or s.line for s in sources])
        sources = '\n'.join([s.line for s in sources])
        return sources, reqs


def write_to_file(path, content):
    f = open(path, 'w')
    f.write(content)
    f.close()

def command():
    c = Command()
    sources, reqs = c.requirements('requirements.github')
    print sources
    write_to_file('requirements.txt', reqs+'\n')


if __name__ == '__main__':
    command()
