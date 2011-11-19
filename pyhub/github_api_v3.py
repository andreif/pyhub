
import json
import urllib2

class GitHubAPI():
    def __init__(self, user, repo, ref=None):
        self.user = user
        self.repo = repo
        self.ref = ref or 'head'
        self.sha = self.get_sha()

    def commits(self):
        return self.get_json(self.get_commits_url())

    def refs(self):
        return self.get_json(self.get_refs_url())

    def get_commits_url(self):
        return 'https://api.github.com/repos/%s/%s/commits/%s' % (self.user, self.repo, self.ref)

    def get_refs_url(self):
        return 'https://api.github.com/repos/%s/%s/git/refs' % (self.user, self.repo)

    def get_tarball_url(self):
        return 'https://nodeload.github.com/%s/%s/tarball/%s' % (self.user, self.repo, self.ref)

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
