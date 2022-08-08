import tempfile
import unittest
import importlib
import sys

# TODO: This is work in progress to show the idea. Need to revisit and implement unit tests for this product
# after https://github.com/USACE/cumulus/issues/260 is closed.
sys.path.append("../")
processor = importlib.import_module('processors.ncep-stage4-mosaic-01h')

src        = './testdata/async_geoprocess/src/cumulus_geoproc/tests/testdata/st4_conus.2022080500.01h.grb2'
dst        = tempfile.mkdtemp()
acquirable = 'ncep-stage4-mosaic-01h'


class TestNcepStage4Mosaic(unittest.TestCase):

    def test_ncep_stage4_mosaic_works(self):
        outfiles = processor.process(src, dst, acquirable)
        self.assertGreaterEqual(len(outfiles), 1)


if __name__ == '__main__':
    unittest.main()
