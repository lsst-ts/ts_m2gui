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

__all__ = ["MainWindow"]

import logging
import sys
import pathlib

from PySide2 import QtCore
from PySide2.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
)

from .utils import set_button
from .layout import LayoutControl, LayoutLocalMode, LayoutControlMode
from . import Model, ControlTabs, LogWindowHandler, SignalMessage, SignalControl


class MainWindow(QMainWindow):
    """Main window of the application.

    Parameters
    ----------
    is_output_log_on_screen : `bool`
        Is outputting the log messages on screen or not.
    log : `logging.Logger` or None, optional
        A logger. If None, a logger will be instantiated. (the default is
        None)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    model : `Model`
        Model class.
    """

    def __init__(self, is_output_log_on_screen, log=None):
        super().__init__()

        # Signal of message
        self._signal_message = SignalMessage()

        # Set the logger
        message_format = "%(asctime)s, %(levelname)s, %(message)s"
        self.log = self._set_log(message_format, is_output_log_on_screen, log=log)

        self.model = Model(self.log)

        # Singal of control
        self._signal_control = SignalControl()

        # Layout of the control panel
        self._layout_control = LayoutControl(self.model, self._signal_control)

        # Layout of the local mode
        self._layout_local_mode = LayoutLocalMode(self.model, self._signal_control)

        # Layout of the control mode
        self._layout_control_mode = LayoutControlMode(self.model, self._signal_control)

        # Control tables
        self._control_tabs = ControlTabs(self.model)
        self._set_control_tabs()

        # Set the main window of application
        self.setWindowTitle("M2 Control")

        # Set the central widget of the Window
        container = QWidget()
        container.setLayout(self._create_layout())
        self.setCentralWidget(container)

        # Set the default conditions
        self._layout_control.set_csc_commander(True)
        self.model.report_config()
        self.model.utility_monitor.report_utility_status()

    def _set_log(self, message_format, is_output_log_on_screen, log=None):
        """Set the logger.

        Parameters
        ----------
        message_format : `str`
            Format of the message.
        is_output_log_on_screen : `bool`
            Is outputting the log messages on screen or not.
        log : `logging.Logger` or None, optional
            A logger. If None, a logger will be instantiated. (the default is
            None)

        Returns
        -------
        log : `logging.Logger`
            A logger.
        """

        if log is None:
            log = logging.getLogger(type(self).__name__)
        else:
            log = log.getChild(type(self).__name__)

        log.addHandler(LogWindowHandler(self._signal_message, message_format))

        if is_output_log_on_screen:
            logging.basicConfig(
                level=logging.INFO,
                handlers=[logging.StreamHandler(sys.stdout)],
                format=message_format,
            )

        return log

    def _set_control_tabs(self):
        """Set the control tables"""

        self._set_tab_overview()
        self._set_tab_alarm_warn()

    def _set_tab_overview(self):
        """Set the table of overview."""

        tab_overview = self._control_tabs.get_tab("Overview")[1]
        tab_overview.set_signal_control(self._signal_control)
        tab_overview.set_signal_message(self._signal_message)

    def _set_tab_alarm_warn(self):
        """Set the table of alarms and warnings."""

        policy_dir = (
            pathlib.Path(__file__).parents[0] / ".." / ".." / ".." / ".." / "policy"
        )
        filepath = policy_dir / "error_code_m2.tsv"

        tab_alarm_warn = self._control_tabs.get_tab("Alarms/Warnings")[1]
        tab_alarm_warn.read_error_list_file(filepath)

    def _create_layout(self):
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()
        layout.addLayout(self._layout_control.layout)
        layout.addLayout(self._layout_local_mode.layout)
        layout.addLayout(self._layout_control_mode.layout)
        layout.addLayout(self._control_tabs.layout)

        button_exit = set_button("Exit", self._callback_exit)
        layout.addWidget(button_exit)

        return layout

    @QtCore.Slot()
    def _callback_exit(self):
        """Exit the application."""

        app = QtCore.QCoreApplication.instance()
        app.quit()
