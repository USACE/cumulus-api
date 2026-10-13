"""
# Initialize Geo Processor Plugins
"""
import pyplugs

geo_procs = pyplugs.names_factory(__package__)
geo_proc = pyplugs.call_factory(__package__)
