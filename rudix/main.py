# -*- coding: utf-8 -*-

'''Rudix Package Manager -- RPM ;D'''

import sys
import os
import optparse

from .core import administrator, __version__, __copyright__, Volume, normalize
from .local import Package, Repository
from .remote import RemotePackage, RemoteRepository


def command_alias(options, args=[]):
    'List aliases.'
    sts = 0
    remote = RemoteRepository()
    if remote.sync() is False:
        return 1
    if not args:
        for alias in remote.aliases:
            print '%s->%s' % (alias, remote.aliases[alias])
    else:
        for alias in args:
            pkg = remote.aliases.get(alias, None)
            if pkg:
                print '%s->%s' % (alias, pkg)
            else:
                print >> sys.stderr, '%s: Not found!' % alias
                sts = 1
    return sts


def command_search(options, args=[]):
    'List all available (remote) packages.'
    sts = 0
    remote = RemoteRepository()
    if remote.sync() is False:
        return 1
    if not args:
        for pkg in remote.packages:
            print pkg
    else:
        for name in args:
            if remote.aliases.has_key(name):
                name = remote.aliases[name]
                print "Using '%s'" % name
            versions = remote.get_versions(name)
            if versions:
                for p in versions:
                    print p.package
            else:
                print >>sys.stderr, "No match for '%s'" % name
                sts = 1
    return sts


def command_list(options, args):
    'List all installed packages.'
    repo = Repository(options.volume)
    repo.sync()
    if not repo.packages:
        print >>sys.stderr, 'No Rudix packages installed.'
        return 1
    for pkg in repo.packages:
        pkg = normalize(pkg)
        if options.verbose:
            p = Package(pkg, volume=options.volume)
            print '%s version %s (install: %s)' % (p.package_id,
                                                   p.version,
                                                   p.install_date)
        else:
            print pkg
    return 0


def command_info(options, args=[]):
    'Show information about installed packages.'
    sts = 0
    if not args:
        repo = Repository(options.volume)
        repo.sync()
        args = repo.packages
    for pkg in args:
        pkg = normalize(pkg)
        p = Package(pkg, volume=options.volume)
        if p.installed is False:
            print >>sys.stderr, "Package '%s' is not installed" % pkg
            sts = 1
            continue
        print '---'
        print 'Name: %s' % p.name
        print 'Version: %s' % p.version
        print 'Install date: %s' % p.install_date
        if options.verbose:
            print 'Package-id: %s' % p.package_id
            print 'Package: %s' % p.package
    return sts


def command_files(options, args=[]):
    "Show package's files."
    sts = 0
    for pkg in args:
        pkg = normalize(pkg)
        p = Package(pkg, volume=options.volume)
        if p.installed is False:
            print >>sys.stderr, "Package '%s' is not installed" % pkg
            sts = 1
            continue
        print p
        for x in p.files:
            if os.path.isdir(x) and not options.verbose:
                continue
            print x
    return sts


def command_download(options, args):
    'Download packages from Internet.'
    sts = 0
    repo = Repository(options.volume)
    repo.sync()
    remote = RemoteRepository()
    if not remote.sync():
        remote = None
    for name in args:
        if os.path.isfile(name):
            print "Found package '%s'" % name
            repo.install_package(name, options.verbose)
        else:
            if remote:
                pkg = remote.match_package(name) or remote.latest_version(name)
                if pkg:
                    print 'Downloading %s...' % pkg.package
                    pkg.download(store_path=pkg.package, verbose=True)
                else:
                    print >>sys.stderr, "No match for '%s'" % name
                    sts = 1
    return sts


@administrator
def command_install(options, args=[]):
    'Install packages from file system or Internet.'
    sts = 0
    repo = Repository(options.volume)
    repo.sync()
    remote = RemoteRepository()
    if not remote.sync():
        remote = None
    for name in args:
        if os.path.isfile(name):
            print "Found package '%s'" % name
            repo.install_package(name, options.verbose)
        else:
            if remote:
                if remote.aliases.has_key(name):
                    name = remote.aliases[name]
                    print "Using '%s'" % name
                pkg = remote.match_package(name) or remote.latest_version(name)
                if pkg:
                    print 'Downloading %s...' % pkg.package
                    repo.remote_install_package(pkg, options.verbose)
                else:
                    print >>sys.stderr, "No match for '%s'" % name
                    sts = 1
    return sts


@administrator
def command_update(options, args):
    'Try to update the current base of packages.'
    repo = Repository(options.volume)
    repo.sync()
    remote = RemoteRepository()
    if not remote.sync():
        return 1
    to_update = []
    for pkg in repo.packages:
        p_local = Package(pkg, volume=options.volume)
        p_remote = remote.latest_version(p_local.name)
        if options.verbose:
            print "Processing package %s:" % p_local.name,
        if p_remote is None:
            if options.verbose:
                print 'No updates available'
            continue
        if version_compare(p_local.version,
                           p_remote.version) >= 0:
            if options.verbose:
                print 'Already in the latest version'
            continue
        if options.verbose:
            print 'New version available'
        print '{0:25} {1:10} will be updated to version {2}'.format(p_local.name,
                                                                    p_local.version,
                                                                    p_remote.version)
        to_update.append(p_remote)
    if not to_update:
        print 'All packages are up to date'
    else:
        total = len(to_update)
        for cnt, p in enumerate(to_update):
            print '[%d/%d] Downloading %s...' % (cnt + 1, total, p.package)
            repo.remote_install_package(p, options.verbose)
    return 0


@administrator
def command_remove(options, args=[]):
    'Remove (uninstall) one or more packages.'
    sts = 0
    for pkg in args:
        pkg = normalize(pkg)
        p = Package(pkg, volume=options.volume)
        if p.installed:
            p.uninstall(options.verbose)
        else:
            if options.verbose:
                print >>sys.stderr, '%s is not installed' % p
            else:
                print >>sys.stderr, "Package '%s' is not installed" % pkg
            sts = 1
    return sts


@administrator
def command_remove_all(options, args=[]):
    'Remove (uninstall) all packages.'
    if not options.force:
        print "Using this option will remove *ALL* Rudix packages!"
        print "Are you sure you want to proceed? (answer 'yes' or 'y' to confirm)"
        answer = raw_input().strip()
        if answer not in ['yes', 'y']:
            print 'Great!'
            return
    print 'Removing package(s)...'
    repo = Repository(options.volume)
    repo.get_packages()
    for pkg in repo.packages:
        p = Package(pkg, volume=options.volume)
        p.uninstall(options.verbose)
    # Remember LinuxConf...
    print 'Cry a little tear, because Rudix is not on this machine anymore...'


def command_status(options, args):
    'Show repositories status.'
    print 'Rudix %s on OS X %s (%s)' % (RudixVersion,
                                        OSXVersion,
                                        OSX.get(OSXVersion, '?'))
    repo = Repository(options.volume)
    repo.sync()
    print repo
    remote = RemoteRepository()
    if remote.sync() is False:
        return 1
    print remote
    if options.verbose:
        if remote.aliases:
            print '%d alias(es)' % len(remote.aliases)
    return 0


def command_search_path(options, args=[]):
    'Search for path in all packages'
    sts = 0
    repo = Repository(options.volume)
    repo.sync()
    for path in args:
        pkgs = repo.search_path(path)
        if pkgs:
            print '%s:' % path,
            for pkg in pkgs:
                print '%s' % pkg,
            print
        else:
            print >>sys.stderr, "No match for '%s'" % path
            sts = 1
    return sts


def command_freeze(options, args=[]):
    'Output installed packages in package file format.'
    repo = Repository(options.volume)
    repo.sync()
    for pkg in repo.packages:
        print Package(pkg, volume=options.volume).package


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    usage = 'Usage: %prog command [options] [arguments]'
    version = 'Rudix Package Manager (%prog) version ' + __version__ + '\n'
    version += __copyright__
    parser = optparse.OptionParser(usage=usage,
                                   version=version)
    parser.add_option('-v', '--verbose', action='store_true', default=False,
                      help='displays more information when available')
    parser.add_option('--volume', default=Volume,
                      help='set volume to use. Default "%default"')
    parser.add_option('--force', action='store_true', default=False,
                      help='force operation')
    commands = optparse.OptionGroup(parser,
                                    'Commands',
                                    'The Package manager commands.')
    commands.add_option('-l', '--list', action='store_const', dest='command',
                        const=command_list,
                        help='list all packages installed')
    commands.add_option('-I', '--info', '--show', action='store_const', dest='command',
                        const=command_info,
                        help='show information about installed packages')
    commands.add_option('-L', '--files', '--content', action='store_const', dest='command',
                        const=command_files,
                        help="show packages's files")
    commands.add_option('-i', '--install', action='store_const', dest='command',
                        const=command_install,
                        help='install local or remote package(s)')
    commands.add_option('-d', '--download', action='store_const', dest='command',
                        const=command_download,
                        help='download package(s) but do not install')
    commands.add_option('-u', '--update', '--upgrade', action='store_const', dest='command',
                        const=command_update,
                        help='update all packages')
    commands.add_option('-r', '--remove', '--uninstall', action='store_const', dest='command',
                        const=command_remove,
                        help='remove (uninstall) package(s)')
    commands.add_option('-R', '--remove-all', '--uninstall-all', action='store_const', dest='command',
                        const=command_remove_all,
                        help='remove (uninstall) ALL packages')
    commands.add_option('-t', '--status', action='store_const', dest='command',
                        const=command_status,
                        help='show repository status')
    commands.add_option('-s', '--search', action='store_const', dest='command',
                        const=command_search,
                        help='search for remote packages')
    commands.add_option('-S', '--search-path', action='store_const', dest='command',
                        const=command_search_path,
                        help='search for path in all packages and print if matched')
    commands.add_option('-a', '--alias', action='store_const', dest='command',
                        const=command_alias,
                        help='list aliases')
    commands.add_option('-z', '--freeze', action='store_const', dest='command',
                        const=command_freeze,
                        help='freeze package list.')
    parser.add_option_group(commands)
    parser.set_defaults(command=command_list)
    # Allow commands without dashes
    if args:
        command = args[0]
        if command.startswith('-') is False:
            args[0] = '--' + command
    (options, args) = parser.parse_args(args)
    return options.command(options, args)
