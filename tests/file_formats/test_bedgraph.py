from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import gzip

import unittest
from chipalign.core.file_formats.bedgraph import BedGraph
from chipalign.core.util import temporary_file
import pandas as pd
from pandas.util.testing import assert_series_equal

class TestBedGraphReading(unittest.TestCase):

    def test_sample_bedgraph_is_read_correctly(self):

        contents = u"chr1\t0\t9959\t0.22042\n" \
                   u"chr1\t9959\t10359\t0.19921\n" \
                   u"chr1\t10359\t10361\t0.22042\n" \
                   u"chr1\t10361\t10438\t0.19921\n"

        expected_series = pd.DataFrame({'chromosome': ['chr1', 'chr1', 'chr1', 'chr1'],
                                        'start': [0, 9959, 10359, 10361],
                                        'end': [9959, 10359, 10361, 10438],
                                        'value': [0.22042, 0.19921, 0.22042, 0.19921]})
        expected_series = expected_series.set_index(['chromosome', 'start', 'end'])
        expected_series = expected_series['value']

        with temporary_file() as tf:
            with open(tf, 'w') as tfh:
                tfh.write(contents)

            bedgraph = BedGraph(tf)
            self.assertTrue(bedgraph.exists())
            bedgraph_as_series = bedgraph.to_pandas_series()

            assert_series_equal(expected_series, bedgraph_as_series,
                                check_series_type=True,
                                check_names=True)

    def test_sample_gzipped_bedgraph_is_read_correctly(self):

        contents = u"chr1\t0\t9959\t0.22042\n" \
                   u"chr1\t9959\t10359\t0.19921\n" \
                   u"chr1\t10359\t10361\t0.22042\n" \
                   u"chr1\t10361\t10438\t0.19921\n"

        expected_series = pd.DataFrame({'chromosome': ['chr1', 'chr1', 'chr1', 'chr1'],
                                        'start': [0, 9959, 10359, 10361],
                                        'end': [9959, 10359, 10361, 10438],
                                        'value': [0.22042, 0.19921, 0.22042, 0.19921]})
        expected_series = expected_series.set_index(['chromosome', 'start', 'end'])
        expected_series = expected_series['value']

        with temporary_file(suffix='.gz') as tf:
            with gzip.GzipFile(tf, 'w') as tfh:
                tfh.write(contents)

            bedgraph = BedGraph(tf)
            self.assertTrue(bedgraph.exists())
            bedgraph_as_series = bedgraph.to_pandas_series()

            assert_series_equal(expected_series, bedgraph_as_series,
                                check_series_type=True,
                                check_names=True)