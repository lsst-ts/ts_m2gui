"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
For more information, see:
https://developer.lsst.io/stack/building-single-package-docs.html
"""

from os import getenv

import lsst.ts.m2gui
from documenteer.conf.pipelinespkg import *

project = "ts_m2gui"
html_theme_options["logotext"] = project
html_title = project
html_short_title = project
doxylink = {}

intersphinx_mapping["ts_m2com"] = ("https://ts-m2com.lsst.io", None)

# Support the sphinx extension of plantuml
extensions.append("sphinxcontrib.plantuml")

# Put the path to plantuml.jar
path_plantuml = (
    "/home/saluser/plantuml.jar"
    if getenv("PATH_PLANTUML") is None
    else getenv("PATH_PLANTUML")
)
plantuml = f"java -jar {path_plantuml}"
