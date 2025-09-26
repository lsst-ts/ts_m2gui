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
import sys

from lsst.ts.guitool import base_frame_run_application
from PySide6.QtCore import QCommandLineOption, QCommandLineParser

from .main_window import MainWindow


def run_application() -> None:
    """Run the application."""
    parser, options = create_parser()
    base_frame_run_application("M2 EUI", parser, options, main)


def create_parser() -> tuple[QCommandLineParser, list[QCommandLineOption]]:
    """Create the command line parser.

    Returns
    -------
    parser : `PySide6.QtCore.QCommandLineParser`
        Command line parser.
    `list` [`PySide6.QtCore.QCommandLineOption`]
        List of command line options.
    """

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

    return parser, [
        option_verbose,
        option_simulation,
        option_log_level,
        option_no_log_file,
        option_is_crio_simulator,
    ]


async def main(
    parser: QCommandLineParser,
    options: list[QCommandLineOption],
    app_close_event: asyncio.Event,
) -> None:
    """Main application.

    Parameters
    ----------
    parser : `PySide6.QtCore.QCommandLineParser`
        Command line parser.
    options : `list` [`PySide6.QtCore.QCommandLineOption`]
        List of command line options.
    app_close_event : `asyncio.Event`
        Event to be set when the application is closing.
    """

    # Get the argument and check the values
    is_verbose = parser.isSet(options[0])
    is_simulation_mode = parser.isSet(options[1])
    log_level = int(parser.value(options[2]))
    is_output_log_to_file = not parser.isSet(options[3])
    is_crio_simulator = parser.isSet(options[4])

    if is_simulation_mode and is_crio_simulator:
        print(
            "No simulation mode and cRIO simulator at the same time.", file=sys.stderr
        )
        return

    # Create a Qt main window, which will be our window.
    window_main = MainWindow(
        is_output_log_to_file,
        is_verbose,
        is_simulation_mode,
        is_crio_simulator=is_crio_simulator,
        log_level=log_level,
    )
    window_main.show()

    await app_close_event.wait()
