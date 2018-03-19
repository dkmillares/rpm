import sys
import os

from .core import Vendor, call_with_output, denormalize, call, is_forbidden


class Package(object):

    """Class that represents a local package."""

    def __init__(self, package_id, volume='/'):
        self.package_id = package_id
        self.volume = volume
        self.name = denormalize(self.package_id)
        self._package = None
        self._version = None
        self._instalL_date = None
        self._files = None
        self._dirs = None

    def __str__(self):
        return "Package '%s' on volume '%s'" % (self.package_id,
                                                self.volume)

    def __repr__(self):
        return "Package('%s')" % (self.package_id)

    @property
    def installed(self):
        cmd = ['pkgutil', '--volume', self.volume,
               '--pkg-info', self.package_id]
        return call(cmd, silent=True)

    @property
    def version(self):
        if not self._version:
            self.get_info()
        return self._version

    @property
    def install_date(self):
        if not self._install_date:
            self.get_info()
        return self._install_date

    @property
    def package(self):
        if not self._package:
            self.get_info()
        self._package = '%s-%s.pkg' % (self.name, self.version)
        return self._package

    @property
    def files(self):
        if not self._files:
            self._files = self.get_files()
        return self._files

    def get_info(self):
        cmd = ['pkgutil', '-v', '--volume', self.volume,
               '--pkg-info', self.package_id]
        out = call_with_output(cmd)
        self._version = '(none)'
        self._install_date = '(none)'
        for line in out:
            line = line.strip()
            if line.startswith('version: '):
                self._version = line[len('version: '):]
            if line.startswith('install-time: '):
                self._install_date = line[len('install-time: '):]
        return self._version, self._install_date

    def get_files(self):
        cmd = ['pkgutil', '--volume', self.volume,
               '--files', self.package_id]
        out = call_with_output(cmd)
        content = [os.path.join(self.volume, line.strip()) for line in out]
        return content

    def uninstall(self, verbose=False):
        dirs = []
        for x in self.files:
            if is_forbidden(x, self.volume):
                if verbose:
                    print "Skipping '%s'" % x
                continue
            if os.path.isdir(x):
                dirs.append(x)
                continue
            if verbose:
                print "Removing '%s'" % x
            try:
                os.unlink(x)
            except OSError as err:
                if verbose:
                    print >> sys.stderr, err
        dirs.sort(lambda p1, p2: p1.count('/') - p2.count('/'), reverse=True)
        for x in dirs:
            if verbose:
                print "Removing directory '%s'" % x
            try:
                os.rmdir(x)
            except OSError as err:
                if verbose:
                    print >> sys.stderr, err
        cmd = ['pkgutil', '--volume', self.volume, '--forget', self.package_id]
        return call(cmd, silent=False)


class Repository(object):

    """Class that represents a local repository."""

    def __init__(self, volume='/', vendor=Vendor):
        self.volume = volume
        self.vendor = vendor
        self.packages = []

    def __str__(self):
        return "%d packages(s) installed on volume '%s'" % (len(self.packages),
                                                            self.volume)

    def __repr__(self):
        return "Repository('%s')" % self.volume

    def sync(self):
        self.get_packages()
        return True

    def get_packages(self):
        cmd = ['pkgutil', '--volume', self.volume,
               '--pkgs=' + self.vendor + '.*']
        out = call_with_output(cmd)
        self.packages = [line.strip() for line in out]
        return self.packages

    def install_package(self, filename, verbose=False):
        cmd = ['installer']
        if verbose:
            cmd.append('-verbose')
        cmd.extend(['-pkg', filename, '-target', self.volume])
        call(cmd, silent=False)

    def remote_install_package(self, remote_package, verbose=False):
        path = remote_package.download(verbose=True)
        self.install_package(path, verbose)
        os.remove(path)

    def search_path(self, path):
        'Search for path in all packages'
        packages = []
        out = call_with_output(['pkgutil', '--file-info', path])
        for line in out:
            line = line.strip()
            if line.startswith('pkgid: '):
                packages.append(line[len('pkgid: '):])
        return packages
