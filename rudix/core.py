# -*- coding: utf-8 -*-

import sys
import os
import re
import subprocess
import platform
import fnmatch

from distutils.version import LooseVersion

__author__ = 'Rudá Moura <ruda.moura@gmail.com>'
__copyright__ = 'Copyright © 2005-2018 Rudá Moura'
__credits__ = 'Rudá Moura, Leonardo Santagada'
__license__ = 'BSD'
__version__ = '2018.3'

Volume = os.getenv('VOLUME', '/')
Vendor = os.getenv('VENDOR', 'org.rudix.pkg')
RudixSite = os.getenv(
    'RUDIX_SITE', 'https://raw.githubusercontent.com/rudix-mac/pkg')
RudixVersion = os.getenv('RUDIX_VERSION', 'master')

OSX = {'10.6': 'Snow Leopard',
       '10.7': 'Lion',
       '10.8': 'Mountain Lion',
       '10.9': 'Mavericks',
       '10.10': 'Yosemite',
       '10.11': 'El Capitan',
       '10.12': 'Sierra',
       '10.13': 'High Sierra'}
try:
    OSXVersion = platform.mac_ver()[0]
except:
    OSXVersion = '(unknown)'
OSXVersion = os.getenv('OSX_VERSION', OSXVersion)

if OSXVersion.count('.') == 2:
    OSXVersion = OSXVersion.rsplit('.', 1)[0]

FORBIDDEN = [
    'Applications',
    'Library',
    'Library/Python',
    'Library/Python/2.?',
    'Library/Python/2.?/site-packages',
    'Network',
    'System',
    'Users',
    'Volumes',
    'bin',
    'cores',
    'dev',
    'etc',
    'home',
    'mach_kernel'
    'net',
    'private',
    'sbin',
    'tmp',
    'usr',
    'var', ]


def is_forbidden(path, volume=Volume):
    for pattern in FORBIDDEN:
        if fnmatch.fnmatch(path, os.path.join(volume, pattern)):
            return True
    return False


def version_compare(v1, v2):
    'Compare software version'
    ver_rel_re = re.compile('([^-]+)(?:-(\d+)$)?')
    v1, r1 = ver_rel_re.match(v1).groups()
    v2, r2 = ver_rel_re.match(v2).groups()
    v_cmp = cmp(LooseVersion(v1), LooseVersion(v2))
    # if they are in the same version, then compare the revision
    if v_cmp == 0:
        if r1 is None:
            r1 = 0
        if r2 is None:
            r2 = 0
        return cmp(int(r1), int(r2))
    else:
        return v_cmp


def normalize(name):
    'Transform package name in package-id.'
    if name.startswith(Vendor) is False:
        package_id = '%s.%s' % (Vendor, name)
    else:
        package_id = name
    return package_id


def denormalize(package_id):
    'Transform package-id in package name.'
    if package_id.startswith(Vendor):
        name = package_id[len(Vendor) + 1:]
    else:
        name = package_id
    return name


def administrator(func):
    'Restrict execution to Administrator (root)'
    if os.getuid() != 0:
        def new_func(*args, **kwargs):
            print >>sys.stderr, 'This operation requires administrator (root) privileges!'
            return 2
    else:
        new_func = func
    return new_func


def call_with_output(args):
    'Call a process and return its output data as a list of strings.'
    try:
        proc = subprocess.Popen(args,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    except OSError as err:
        print >> sys.stderr, err, ': ' + ' '.join(args)
        return []
    return proc.communicate()[0].splitlines()


def call(args, silent=True):
    'Call a process and return its status.'
    try:
        if silent:
            with open('/dev/null') as dev_null:
                sts = subprocess.call(args, stdout=dev_null, stderr=dev_null)
        else:
            sts = subprocess.call(args)
    except OSError as err:
        print >> sys.stderr, err, ': ' + ' '.join(args)
        sts = 1
    return True if sts == 0 else False
