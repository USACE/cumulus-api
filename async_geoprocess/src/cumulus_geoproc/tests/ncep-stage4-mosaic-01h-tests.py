import tempfile
import unittest
import importlib
import sys

sys.path.append("../")
processor = importlib.import_module('processors.ncep-stage4-mosaic-01h')

src        = './testdata/async_geoprocess/src/cumulus_geoproc/tests/testdata/st4_conus.2022080500.01h.grb2'
dst        = tempfile.mkdtemp()
acquirable = 'ncep-stage4-mosaic-01h'


class TestNcepStage4Mosaic(unittest.TestCase):

    def test_ncep_stage4_mosaic_works(self):
        outfiles = processor.process(src, dst, acquirable)
        print(outfiles)


if __name__ == '__main__':
    unittest.main()
