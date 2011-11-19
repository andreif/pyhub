import os
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
        os.system('mv %s/%s-%s-* %s ' % (self.path, self.github.user, self.github.repo, self.get_unpack_path()))
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