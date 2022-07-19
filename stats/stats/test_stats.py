import unittest
import json
import stats

class TestStats(unittest.TestCase):

    def test_smokey(self):
        msg = json.dumps(
            {
                "geometry_url": "https://water-api.corps.cloud/watersheds/upper-mississippi-river/geometry",
                "raster_info": {
                    "bucket": "castle-data-develop",
                    "key": "MRMS_MultiSensor_QPE_01H_Pass1_00.00_20220718-170000.tif"
                },
                "output_url": "https://mimir.corps.cloud/v1/write"
            }
        )
        stats.handle_message(msg)
        
        self.assertIsNotNone(msg)

if __name__ == '__main__':
    unittest.main()