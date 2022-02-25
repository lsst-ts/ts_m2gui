#!/usr/bin/env python
# This file is part of ts_m2gui.
#
# Developed for the LSST Telescope and Site Subsystem.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

import argparse
from PySide2.QtWidgets import QApplication

from lsst.ts.m2gui import MainWindow

# Set the parser
parser = argparse.ArgumentParser(description="Run M2 graphical user interface (GUI).")

parser.add_argument(
    "--verbose", default=False, action="store_true", help="Output the log on screen.",
)

# Get the arguments
args = parser.parse_args()

# You need one (and only one) QApplication instance per application.
app = QApplication([])

# Create a Qt main window, which will be our window.
window_main = MainWindow(args.verbose)
window_main.show()

# Start the event loop.
app.exec_()

# Your application won't reach here until you exit and the event
# loop has stopped.
