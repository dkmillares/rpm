import unittest

from rudix.local import *


class PackageTests(unittest.TestCase):

    def setUp(self):
        self.xyz = Package('org.rudix.pkg.xyz')
        self.foo = Package('org.rudix.pkg.static-foo')

    def test_name(self):
        self.assertEqual(self.xyz.name, 'xyz')
        self.assertEqual(self.foo.name, 'static-foo')

    def test_version(self):
        self.assertEqual(self.xyz.version, '(none)')
        self.assertEqual(self.foo.version, '(none)')


if __name__ == '__main__':
    unittest.main()
