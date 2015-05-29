from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import os
import tempfile
import luigi
from chipalign.core.downloader import fetch
from chipalign.genome.genome_alignment import DownloadedConsolidatedReads
from chipalign.genome.genome_signal import Signal
from chipalign.roadmap_data.downloaded_signal import DownloadedSignal
from tests.helpers.task_test import TaskTestCase
from tests.roadmap_compatibility.roadmap_tag import roadmap_test
from chipalign.core.util import temporary_file
from itertools import izip

@roadmap_test
class TestMacsPileup(TaskTestCase):

    _CELL_TYPE = 'E008'
    _TRACK = 'H3K56ac'
    _GENOME_VERSION = 'hg19'
    _CHROMOSOMES = 'male'


    @classmethod
    def setUpClass(cls):
        from chipalign.command_line_applications.ucsc_suite import bigWigToBedGraph
        from chipalign.command_line_applications.common import sort

        if cls._GENOME_VERSION != 'hg19':
            raise NotImplementedError('Cannot do this for non hg19')

        answer_url = 'http://egg2.wustl.edu/roadmap/data/byFileType/signal/consolidated/macs2signal/pval/' \
                     '{}-{}.pval.signal.bigwig'.format(cls._CELL_TYPE, cls._TRACK)

        with temporary_file(prefix='tmp-signal', suffix='.bigWig') as tmp_bigwig_file:

            with open(tmp_bigwig_file, 'w') as f:
                fetch(answer_url, f)

            with temporary_file(prefix='tmp-signal', suffix='.bdg') as tmp_bdg_file:
                bigWigToBedGraph(tmp_bigwig_file, tmp_bdg_file)

                __, cls.answer_file = tempfile.mkstemp(prefix='tmp-TestMacsPileup-answer')
                sort(tmp_bdg_file, '-k1,1', '-k2,2n', '-k3,3n', '-k5,5n',
                     '-o', cls.answer_file)

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink(cls.answer_file)
        except OSError:
            if os.path.isfile(cls.answer_file):
                raise

    def test_downloaded_signal_task_downloads_correctly(self):

        ds = DownloadedSignal(cell_type=self._CELL_TYPE,
                              track=self._TRACK,
                              genome_version=self._GENOME_VERSION,
                              chromosomes=self._CHROMOSOMES)

        luigi.build([ds], local_scheduler=True)

        self.assertTrue(ds.complete())


        with ds.output().open('r') as actual:
            with open(self.answer_file) as expected:

                for expected_row, actual_row in izip(expected, actual):
                    self.assertEquals(expected_row, actual_row)

                # Check that files were read completely (`izip` stops when one of them stops)
                self.assertRaises(StopIteration, actual.next)
                self.assertRaises(StopIteration, expected.next)

    def test_can_reproduce_signal_track(self):


        input_reads = DownloadedConsolidatedReads(genome_version=self._GENOME_VERSION,
                                                  cell_type=self._CELL_TYPE,
                                                  track='Input',
                                                  chromosomes=self._CHROMOSOMES
                                                  )

        track_reads = DownloadedConsolidatedReads(genome_version=self._GENOME_VERSION,
                                                  cell_type=self._CELL_TYPE,
                                                  track=self._TRACK,
                                                  chromosomes=self._CHROMOSOMES
                                                  )

        st = Signal(input_task=input_reads, treatment_task=track_reads)
        self.build_task(st)

        with st.output().open('r') as actual:
            with open(self.answer_file) as expected:
                for expected_row, actual_row in izip(expected, actual):

                    expected_chromosome, expected_start, expected_end, expected_score = expected_row.strip('\n').split('\t')
                    actual_chromosome, actual_start, actual_end, actual_score = actual_row.strip('\n').split('\t')

                    expected_start, actual_start = int(expected_start), int(actual_start)
                    expected_end, actual_end = int(expected_end), int(actual_end)
                    expected_score, actual_score = float(expected_score), float(actual_score)

                    message = '{!r} != {!r}'.format(expected_row, actual_row)

                    self.assertEquals(expected_chromosome, actual_chromosome, message)
                    self.assertEquals(expected_start, actual_start, message)
                    self.assertEquals(expected_end, actual_end, message)

                    # They round to four digits, but there are some weird things going on with rounding there
                    # So let's just do three
                    self.assertAlmostEqual(expected_score, actual_score, msg=message, places=3)

                # Check that files were read completely (`izip` stops when one of them stops)
                self.assertRaises(StopIteration, actual.next)
                self.assertRaises(StopIteration, expected.next)
