"""Geoprocess init
"""


"""
Product example message:

    {
        "geoprocess": "incoming-file-to-cogs",
        "geoprocess_config": {
            "acquirablefile_id": "11a69c52-3a59-4c50-81a6-eba26e6573d4",
            "acquirable_id": "2429db9a-9872-488a-b7e3-de37afc52ca4",
            "acquirable_slug": "cbrfc-mpe",
            "bucket": "castle-data-develop",
            "key": "cumulus/acquirables/cbrfc-mpe/xmrg0322202216z.grb"
    }

SNODAS example message:

    {
        'geoprocess': 'snodas-interpolate',
        'geoprocess_config': {
            'bucket': 'castle-data-develop',
            'datetime': '20220323',
            'max_distance': 16
        }
    }

"""
