# emacs: -*- mode: python-mode; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# ex: set sts=4 ts=4 sw=4 noet:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Test XMP parser"""


from shutil import copy
from os.path import dirname
from os.path import join as opj
from datalad.api import Dataset
from datalad.tests.utils import with_tempfile
from datalad.tests.utils import ok_clean_git
from datalad.tests.utils import assert_status
from datalad.tests.utils import assert_result_count


@with_tempfile(mkdir=True)
def test_xmp(path):
    ds = Dataset(path).create()
    ds.config.add('datalad.metadata.nativetype', 'xmp', where='dataset')
    copy(
        opj(dirname(dirname(dirname(__file__))), 'tests', 'data', 'xmp.pdf'),
        path)
    ds.add('.')
    ok_clean_git(ds.path)
    res = ds.aggregate_metadata()
    assert_status('ok', res)
    res = ds.metadata('xmp.pdf')
    assert_result_count(res, 1)
    # compare full expected metadata set to catch any change of mind on the
    # side of the XMP library
    assert_result_count(
        res, 1,
        metadata={
            'dc:creator': 'Michael Hanke',
            'dc:description': 'dlsubject',
            'dc:description<?xml:lang>': 'x-default',
            'dc:title': 'dltitle',
            'dc:title<?xml:lang>': 'x-default',
            'pdfaid:part': '1',
            'pdfaid:conformance': 'A',
            'pdf:Keywords': 'dlkeyword1 dlkeyword2',
            'pdf:Producer': 'LibreOffice 5.2',
            'xmp:CreateDate': '2017-10-08T10:27:06+02:00',
            'xmp:CreatorTool': 'Writer',
        })
