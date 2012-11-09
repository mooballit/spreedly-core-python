# Copyright (c) 2012 Mooball IT
# See also LICENSE.txt
import doctest
import spreedlycore
import unittest


OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    spreedlycore,
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocTestSuite(
            docfile,
            optionflags=OPTIONFLAGS,
            ) for docfile in DOCFILES]
    )
    return suite
