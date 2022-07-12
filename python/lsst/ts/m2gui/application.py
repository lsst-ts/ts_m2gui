# This file is part of ts_m2gui.
#
# Developed for the LSST Data Management System.
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
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["run_application"]

from PySide2.QtCore import QCommandLineParser, QCommandLineOption
from PySide2.QtWidgets import QApplication

from . import MainWindow


def run_application(argv):
    """Run the application.

    Parameters
    ----------
    argv : `list`
        Arguements from the command line.
    """

    # You need one (and only one) QApplication instance per application.
    app = QApplication(argv)
    app.setApplicationName("M2 EUI")

    # Set the parser
    parser = QCommandLineParser()
    parser.setApplicationDescription("Run the M2 graphical user interface (GUI).")
    parser.addHelpOption()

    option_verbose = QCommandLineOption(["v", "verbose"], "Output the log on screen.")
    parser.addOption(option_verbose)

    parser.process(app)

    # Get the argument
    is_verbose = parser.isSet(option_verbose)

    # Create a Qt main window, which will be our window.
    window_main = MainWindow(is_verbose)
    window_main.show()

    # Start the event loop.
    app.exec_()

    # Your application won't reach here until you exit and the event
    # loop has stopped.
