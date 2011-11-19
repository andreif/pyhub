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

import json
import urllib2
import os
import re
import sys

from github_api_v3 import GitHubAPI

class GitHubRepo():
    
    def __init__(self, user, repo, ref=None):
        self.github = GitHubAPI(user=user, repo=repo, ref=ref)
        self.user = user
        self.repo = repo
        self.ref = ref or 'head'
        self.sha = self.get_sha()
        self.path = './src'
        self.download_and_unpack()

#    def get_sha1(self):
#        raw_json = urllib2.urlopen(self.get_commits_url()).read()
#        return json.loads(raw_json)['sha']

    def get_json(self, url):
        return json.loads(urllib2.urlopen(url).read())

    def find_ref_in(self, where):
        if where == 'commits':
            ref = self.get_json(self.get_commits_url())
            if ref.get('message') != 'Not Found':
                return ref
        else:
            try:
                for ref in self.get_json(self.get_refs_url() + '/' + where):
                    name = ref['ref'].split('/',2)[-1]
                    if name == self.ref:
                        return ref
            except urllib2.HTTPError:
                pass

    def get_sha(self):
        ref = self.find_ref_in('commits')#self.find_ref_in('heads') or self.find_ref_in('tags') or
        if ref:
            return ref.get('sha') or ref['object']['sha']
        else:
            raise Exception('Ref was not found: %s' % self.ref)

    def get_commits_url(self):
        return 'https://api.github.com/repos/%s/%s/commits/%s' % (self.user, self.repo, self.ref)

    def get_refs_url(self):
        return 'https://api.github.com/repos/%s/%s/git/refs' % (self.user, self.repo)

    def get_tarball_url(self):
        return 'https://nodeload.github.com/%s/%s/tarball/%s' % (self.user, self.repo, self.ref)

    def download_and_unpack(self):
        if self.downloaded(): return
        if not os.path.exists(self.path): os.makedirs(self.path)
        self.remove_old_versions()
        #print self.get_tarball_url()
        os.system('curl %s | tar xz --directory=%s' % (
            self.get_tarball_url(),
            self.path
        ))
        os.system('mv %s/%s-%s-* %s' % (self.path, self.user, self.repo, self.unpack_dir()))
        if not self.downloaded():
            raise Exception('Failed to download github repo %s for sha %s' % (self.repo, self.sha[0:7]))

    def downloaded(self):
        return os.path.exists(self.unpack_dir())

    def remove_old_versions(self):
        os.system('rm -r %s/%s-%s-*' % (self.path, self.user, self.repo))

    def unpack_dir(self):
        return '%s/%s-%s-%s' % (
            self.path,
            self.user,
            self.repo,
            self.sha[0:7]
        )

    def line(self):
        return '-e ' + self.unpack_dir()

    def req(self):
        return '-e git+git@github.com:%s/%s.git@%s#egg=%s-dev' % (
            self.user,
            self.repo,
            self.sha,
            self.repo
        )


class Source():
    
    def __init__(self, str):
        self.line = ''
        self.req = ''
        self.parse(str)

    def parse(self, str):
        if str.startswith('github:'):
            repo = self.parse_github(str[7:])
            self.line = repo.line()
            self.req = repo.req()
        elif str.startswith('bitbucket:'):
            pass
        else:
            self.line = str

    def parse_github(self, str):
        m = re.search(r'(?P<user>\S+)/(?P<repo>\S+)(\s*@(?P<ref>\S+))?', str)
        return GitHubRepo(user=m.group('user'), repo=m.group('repo'), ref=m.group('ref'))


class Command():
    def requirements(self, filename):
        source_file = open(filename)
        sources = []
        lines = source_file.read().split('\n')
        for line in lines:
            line = line.split('#')[0].strip()
            if len(line):
                try:
                    sources.append(Source(line))
                except Exception as e:
                    sys.stderr.write('%s %s' % (line, e))
        self.reqs = '\n'.join([s.req or s.line for s in sources])
        return '\n'.join([s.line for s in sources])


if __name__ == '__main__':
    c = Command()
    sources = c.requirements(sys.argv[1])
    if len(sys.argv) > 2:
        f = open(sys.argv[2], 'w')
        f.write(sources+'\n')
        f.close()
    if len(sys.argv) > 3:
        f = open(sys.argv[3], 'w')
        f.write(c.reqs+'\n')
        f.close()
    print sources
