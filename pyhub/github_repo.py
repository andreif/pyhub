import os
import re
from github_api_v3 import GitHubAPI
from utils import read_file, write_file

class GitHubRepo():

    def __init__(self, user, repo, ref=None):
        self.github = GitHubAPI(user=user, repo=repo, ref=ref)
        self.path = './src'
        self.download_and_unpack()
        self.patch_version_info()

    def download_and_unpack(self):
        if self.downloaded(): return
        if not os.path.exists(self.path): os.makedirs(self.path)
        self.remove_old_versions()
        os.system('curl %s | tar xz --directory=%s' % (
            self.github.get_tarball_url(),
            self.path
        ))
        self.rename_unpacked_dir()
        if not self.downloaded():
            raise Exception('Failed to download github repo "%s" for sha %s' % (self.github.repo, self.github.short_sha()))

    def rename_unpacked_dir(self):
        os.system('mv %s/%s-%s-* %s ' % (self.path, self.github.user, self.github.repo, self.get_unpack_path()))

    def patch_version_info(self):
        path = self.get_unpack_path() + '/setup.py'
        setup = read_file(path)
        setup = re.sub(
            r'version\s*=\s*[\'\"]([^\'\"]+)[\'\"]',
            "version = '\\1-%s-%s-%s'" % (self.github.user, self.github.repo, self.github.short_sha()),
            setup
        )
        if 'download_url' in setup:
            setup = re.sub(
                r'download_url\s*=\s*[\'\"][^\'\"]+[\'\"]',
                "download_url = 'git@github.com:%s/%s.git'" % (self.github.user, self.github.repo),
                setup
            )
        else:
            setup = re.sub(
                r'(([^\n]*)version\s*=[^\n]*)',
                "\\1\n\\2download_url = 'git@github.com:%s/%s.git'," % (self.github.user, self.github.repo),
                setup
            )
        write_file(path, setup)
        write_file(self.get_unpack_path() + '/.pyhub', self.get_nice_ref())

    def get_nice_ref(self):
        return '%s/%s @%s' % (self.github.user, self.github.repo, self.github.ref)

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
        return self.get_unpack_path()

    def req(self):
        return '-e git+git@github.com:%s/%s.git@%s#egg=%s-dev' % (
            self.github.user,
            self.github.repo,
            self.github.commit_sha,
            self.github.repo
        )
