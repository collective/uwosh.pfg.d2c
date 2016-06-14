# -*- coding: utf-8 -*-

import unittest
import doctest
from plone.testing import layered

from .testing import D2C_FUNCTIONAL_TESTING

testfiles = (
    'browser.txt',
)

def test_suite():
    return unittest.TestSuite([
        layered(doctest.DocFileSuite(
            f, package='uwosh.pfg.d2c.tests',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            layer=D2C_FUNCTIONAL_TESTING)
            for f in testfiles
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
