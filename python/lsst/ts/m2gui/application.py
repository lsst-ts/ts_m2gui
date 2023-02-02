# This file is part of ts_m2gui.
#
# Developed for the LSST Telescope and Site Systems.
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

import asyncio
import functools
import os
import sys

import qasync
from PySide2.QtCore import QCommandLineOption, QCommandLineParser

from . import MainWindow


def run_application(argv):
    """Run the application.

    Parameters
    ----------
    argv : `list`
        Arguments from the command line.
    """

    if "QT_API" not in os.environ:
        os.environ.setdefault("QT_API", "PySide2")
        print("qasync: QT_API not set, defaulting to PySide2.")

    try:
        qasync.run(main(argv))
    except asyncio.exceptions.CancelledError:
        sys.exit(0)


async def main(argv):
    """Main application.

    Parameters
    ----------
    argv : `list`
        Arguments from the command line.
    """

    # The set of "aboutToQuit" comes from "qasync/examples/aiohttp_fetch.py"
    loop = asyncio.get_event_loop()
    future = asyncio.Future()

    # You need one (and only one) QApplication instance per application.
    # There is one QApplication instance in "qasync" already.
    app = qasync.QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(
            functools.partial(close_future, future, loop)
        )

    app.setApplicationName("M2 EUI")

    # Set the parser
    parser = QCommandLineParser()
    parser.setApplicationDescription("Run the M2 graphical user interface (GUI).")
    parser.addHelpOption()

    option_verbose = QCommandLineOption(
        ["v", "verbose"], "Print log messages to terminal."
    )
    parser.addOption(option_verbose)

    option_simulation = QCommandLineOption(
        ["s", "simulation"], "Run the simulation mode."
    )
    parser.addOption(option_simulation)

    option_log_level = QCommandLineOption(
        ["d", "debuglevel"],
        (
            "Debug logging level: CRITICAL (50), ERROR (40), WARNING (30), "
            "INFO (20), DEBUG (10), NOTSET (0). The default is 20."
        ),
        "level",
        "20",
    )
    parser.addOption(option_log_level)

    option_no_log_file = QCommandLineOption(
        ["no-logfile"], "Do not write log messages to file."
    )
    parser.addOption(option_no_log_file)

    option_is_crio_simulator = QCommandLineOption(
        ["use-crio-simulator"],
        "Use the M2 cRIO simulator. This is different from the simulation mode.",
    )
    parser.addOption(option_is_crio_simulator)

    parser.process(app)

    # Get the argument and check the values
    is_output_log_to_file = not parser.isSet(option_no_log_file)
    is_verbose = parser.isSet(option_verbose)
    is_simulation_mode = parser.isSet(option_simulation)
    log_level = int(parser.value(option_log_level))
    is_crio_simulator = parser.isSet(option_is_crio_simulator)

    if is_simulation_mode and is_crio_simulator:
        print("No simulation mode and cRIO simulator at the same time.")
        sys.exit(0)

    # Create a Qt main window, which will be our window.
    window_main = MainWindow(
        is_output_log_to_file,
        is_verbose,
        is_simulation_mode,
        is_crio_simulator=is_crio_simulator,
        log_level=log_level,
    )
    window_main.show()

    await future

    # Your application won't reach here until you exit and the event
    # loop has stopped.
    return True


def close_future(future, loop):
    """Close the future.

    This is needed to ensure that all pre- and post-processing for the event
    loop is done. See the source code in qasync library for the details.

    Parameters
    ----------
    future : `asyncio.Future`
        Future.
    loop : `asyncio.unix_events._UnixSelectorEventLoop`
        Event loop.
    """

    loop.call_later(10, future.cancel)
    future.cancel()
