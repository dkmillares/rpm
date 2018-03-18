import unittest

from rudix.core import *
from rudix.local import *

class FunctionTests(unittest.TestCase):

    def test_version_compare(self):
        self.assertEqual(version_compare('1.0', '2.0'), -1)
        self.assertEqual(version_compare('1.0', '1.0.1'), -1)
        self.assertEqual(version_compare('1.0.2', '1.0.10'), -1)
        self.assertEqual(version_compare('1.0.1-2', '1.0.1-10'), -1)
        self.assertEqual(version_compare('1.11-1', '1.11.1-0'), -1)
        self.assertEqual(version_compare('2.1.0b1-0', '2.1.2-0'), -1)
        self.assertEqual(version_compare('2.2.1-10', '3.0-0'), -1)
        self.assertEqual(version_compare('1.0-1', '1.0.1'), -1)
        self.assertEqual(version_compare('1.0-3', '1.0.2'), -1)
        self.assertEqual(version_compare('1.0', '1.0-1'), -1)
        self.assertEqual(version_compare('1.0.2', '1.0.10'), -1)
        self.assertEqual(version_compare('1.0.1-2', '1.0.1-10'), -1)
        self.assertEqual(version_compare('R13B', 'R14B'), -1)
        self.assertEqual(version_compare('1.0.1', '1.0.1-0'), 0)
        self.assertEqual(version_compare('7.2', '7.2e'), -1)
        self.assertEqual(version_compare('7.2d', '7.2e'), -1)
        self.assertEqual(version_compare('7.2e', '7.4.0'), -1)
        self.assertEqual(version_compare('1.9a', '2.0'), -1)
        self.assertEqual(version_compare('1.8.10', '3.0b2'), -1)
        self.assertEqual(version_compare('2014z', '2015a'), -1)
        self.assertEqual(version_compare('2014.10', '2015.6.1'), -1)
        self.assertEqual(version_compare('2015.6.1', '2015.7'), -1)
        self.assertEqual(version_compare('2015.6.1', '2015.10.20'), -1)
        self.assertEqual(version_compare('1.10.1', '1.2'), 1)

    def test_sort_version(self):
        l = ['1.0', '1.0-2', '1.0.1', '1.2', '1.7', '1.7.1']
        l2 = sorted(l, cmp=version_compare)
        for i in zip(l,l2):
            self.assertEqual(i[0], i[1])

    def test_normalization(self):
        self.assertEqual(normalize('rudix'),
                         'org.rudix.pkg.rudix')
        self.assertEqual(normalize('org.rudix.pkg.rudix'),
                         'org.rudix.pkg.rudix' )

    def test_denormalization(self):
        self.assertEqual(denormalize('org.rudix.pkg.rudix'), 'rudix')
        self.assertEqual(denormalize('rudix'), 'rudix')

class PackageTests(unittest.TestCase):

    def setUp(self):
        self.xyz = Package('org.rudix.pkg.xyz')
        self.foo = Package('org.rudix.pkg.static-foo')

    def test_name(self):
        self.assertEqual(self.xyz.name, 'xyz')
        self.assertEqual(self.foo.name, 'static-foo')

if __name__ == '__main__':
    unittest.main()
