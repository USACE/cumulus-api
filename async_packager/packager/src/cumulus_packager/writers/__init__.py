"""Initialize Packager Plugins
"""
import pyplugs

pkg_writers = pyplugs.names_factory(__package__)
pkg_writer = pyplugs.call_factory(__package__)
