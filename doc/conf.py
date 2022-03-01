"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
For more information, see:
https://developer.lsst.io/stack/building-single-package-docs.html
"""

from documenteer.conf.pipelinespkg import *
import lsst.ts.m2gui

project = "ts_m2gui"
html_theme_options["logotext"] = project
html_title = project
html_short_title = project
doxylink = {}
