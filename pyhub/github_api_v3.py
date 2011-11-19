
import json
import urllib2

class GitHubAPI():
    def __init__(self, user, repo, ref=None):
        self.user = user
        self.repo = repo
        self.ref = ref or 'HEAD'
        self.commit_sha = None
        self.sha = self.get_sha()

    def short_sha(self, length=7):
        return self.commit_sha[0:length]

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
        shas = []
        ref = self.get_json(self.get_commits_url())
        if ref.get('message') == 'Not Found':
            raise Exception('Commit sha not found for ref: %s' % self.ref)
        else:
            shas.append(ref['sha'])
            self.commit_sha = ref['sha']
        for where in ['heads', 'tags']:
            try:
                for ref in self.get_json(self.get_refs_url() + '/' + where):
                    name = ref['ref'].split('/',2)[-1]
                    if name == self.ref:
                        shas.append(ref['object']['sha'])
            except urllib2.HTTPError:
                pass
        shas = list(set(shas))
        if shas:
            return shas
        else:
            raise Exception('Ref was not found: %s' % self.ref)
