import sys
import os
import re
import tempfile

from .core import RudixSite, RudixVersion, OSXVersion, administrator, call, call_with_output


class RemotePackage(object):

    """Class that represents a remote package."""

    def __init__(self,
                 package,
                 site_url=RudixSite,
                 rudix_version=RudixVersion,
                 osx_version=OSXVersion):
        self.package = package
        url = '{base}/{rudix}'
        self.url = url.format(base=site_url,
                              rudix=rudix_version,
                              osx=osx_version)
        self._name = None
        self._version = None
        self._revision = None

    def __str__(self):
        return "Package '%s' on '%s'" % (self.package, self.url)

    def __repr__(self):
        return "RemotePackage('%s')" % self.package

    @property
    def package_id(self):
        if self._name is None:
            self.split()
        return normalize(self._name)

    @property
    def name(self):
        if self._name is None:
            self.split()
        return self._name

    @property
    def version(self):
        if self._version is None:
            self.split()
        return '%s-%s' % (self._version, self._revision)

    def split(self):
        pat = re.compile(r'^(.+)-([^-]+)\.pkg$')
        self._name, self._version, = pat.match(self.package).groups()
        self._revision = 999
        return self._name, self._version, self._revision

    def download(self, store_path=None, verbose=False):
        tempf = None
        if store_path is None:
            tempf, file_path = tempfile.mkstemp(suffix=self.package)
            store_path = file_path
        url = self.url + '/{package}'
        url = url.format(package=self.package)
        cmd = ['curl', url, '--output', store_path,
               '--remote-time', '--continue-at', '-', '--location']
        if verbose:
            cmd.append('--progress-bar')
        else:
            cmd.append('--silent')
        call(cmd, silent=False)
        if tempf:
            os.close(tempf)
        return store_path


class RemoteRepository(object):

    """Class that represents a remote repository."""

    def __init__(self,
                 site_url=RudixSite,
                 rudix_version=RudixVersion,
                 osx_version=OSXVersion):
        self.site_url = site_url
        self.rudix_version = rudix_version
        self.osx_version = osx_version
        url = '{base}/{rudix}'
        self.url = url.format(base=self.site_url,
                              rudix=self.rudix_version,
                              osx=self.osx_version)
        self.aliases = {}
        self.packages = []

    def __str__(self):
        return "%d package(s) available on '%s'" % (len(self.packages),
                                                    self.url)

    def __repr__(self):
        return "RemoteRepository('%s')" % self.url

    def _retrieve_manifest(self):
        url = self.url + '/00MANIFEST.txt'
        cmd = ['curl', '-s', url]
        content = call_with_output(cmd)
        if not content:
            return False
        for line in content:
            if line.endswith('.pkg'):
                self.packages.append(line)
        return True

    def _retrieve_aliases(self):
        url = self.url + '/00ALIASES.txt'
        cmd = ['curl', '-s', url]
        content = call_with_output(cmd)
        if not content:
            return False
        for line in content:
            if '->' in line:
                alias, pkg = line.split('->')
                self.aliases[alias] = pkg

    def sync(self):
        status = self._retrieve_manifest()
        if status is False:
            print >> sys.stderr, "Could not synchronize with '%s'" % self.site_url
            return False
        status = self._retrieve_aliases()
        return True

    def match_package(self, pkg):
        if pkg in self.packages:
            return RemotePackage(pkg)
        else:
            return None

    def get_versions(self, name):
        versions = []
        for pkg in self.packages:
            p = RemotePackage(pkg)
            if name == p.name:
                versions.append(p)
        if versions:
            versions = sorted(list(set(versions)),
                              reverse=True,
                              cmp=lambda x, y: version_compare(x.version,
                                                               y.version))
            return versions
        else:
            return []

    def latest_version(self, name):
        versions = self.get_versions(name)
        return versions[0] if versions else None
