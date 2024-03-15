"""Sphinx configuration file for an LSST stack package.

This configuration only affects single-package Sphinx documentation builds.
For more information, see:
https://developer.lsst.io/stack/building-single-package-docs.html
"""

import lsst.ts.m2gui  # type: ignore # noqa
from documenteer.conf.pipelinespkg import *  # type: ignore # noqa

project = "ts_m2gui"
html_theme_options["logotext"] = project  # type: ignore # noqa
html_title = project
html_short_title = project
doxylink = {}  # type: ignore # noqa

intersphinx_mapping["ts_m2com"] = ("https://ts-m2com.lsst.io", None)  # type: ignore # noqa

# Support the sphinx extension of mermaid
extensions = [
    "sphinxcontrib.mermaid",
    "sphinx_automodapi.automodapi",
]
