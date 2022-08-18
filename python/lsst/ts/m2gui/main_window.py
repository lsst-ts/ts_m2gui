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

from qasync import asyncSlot, QApplication

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QMessageBox,
)

from lsst.ts.m2com import read_yaml_file

from .controltab import TabSettings
from .layout import LayoutControl, LayoutLocalMode, LayoutControlMode
from . import (
    Model,
    ControlTabs,
    LogWindowHandler,
    SignalMessage,
    run_command,
)


class MainWindow(QMainWindow):
    """Main window of the application.

    Parameters
    ----------
    is_output_log_on_screen : `bool`
        Is outputting the log messages on screen or not.
    is_simulation_mode: `bool`
        Is the simulation mode or not.
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

    def __init__(self, is_output_log_on_screen, is_simulation_mode, log=None):
        super().__init__()

        # Signal of message
        self._signal_message = SignalMessage()

        # Set the logger
        message_format = "%(asctime)s, %(levelname)s, %(message)s"
        self.log = self._set_log(message_format, is_output_log_on_screen, log=log)

        self.model = self._set_model(is_simulation_mode)

        # Layout of the control panel
        self._layout_control = LayoutControl(self.model)

        # Layout of the local mode
        self._layout_local_mode = LayoutLocalMode(self.model)

        # Layout of the control mode
        self._layout_control_mode = LayoutControlMode(self.model)

        # Control tables
        self._control_tabs = ControlTabs(self.model)
        self._set_control_tabs()

        # Table to have the settings
        self._tab_settings = TabSettings("Settings", self.model)

        # Set the main window of application
        self.setWindowTitle("M2 Control")

        # Set the central widget of the Window
        container = QWidget()
        container.setLayout(self._create_layout())
        self.setCentralWidget(container)

        # Disable the Qt close button
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint
        )

        self._add_tool_bar()

        self._set_default()

        if is_simulation_mode:
            self.log.info("Running the simulation mode.")

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

    def _set_model(self, is_simulation_mode):
        """Set the model.

        Parameters
        ----------
        is_simulation_mode: `bool`
            Is the simulation mode or not.

        Returns
        -------
        model : `Model`
            Model object.
        """

        # Read the yaml file
        filepath = self._get_policy_dir() / "default.yaml"
        default_settings = read_yaml_file(filepath)

        model = Model(
            self.log,
            host=default_settings["host"],
            port_command=default_settings["port_command"],
            port_telemetry=default_settings["port_telemetry"],
            timeout_connection=default_settings["timeout_connection"],
            is_simulation_mode=is_simulation_mode,
        )

        return model

    def _set_control_tabs(self):
        """Set the control tables"""

        self._set_tab_overview()
        self._set_tab_alarm_warn()
        self._set_tab_cell_status()

    def _set_tab_overview(self):
        """Set the table of overview."""

        tab_overview = self._control_tabs.get_tab("Overview")[1]
        tab_overview.set_signal_control(self.model.signal_control)
        tab_overview.set_signal_message(self._signal_message)

    def _set_tab_alarm_warn(self):
        """Set the table of alarms and warnings."""

        filepath = self._get_policy_dir() / "error_code_m2.tsv"

        tab_alarm_warn = self._control_tabs.get_tab("Alarms/Warnings")[1]
        tab_alarm_warn.read_error_list_file(filepath)

    def _get_policy_dir(self):
        """Get the policy directory.

        Returns
        -------
        `pathlib.Path`
            Policy directory.
        """

        return pathlib.Path(__file__).parents[0] / ".." / ".." / ".." / ".." / "policy"

    def _set_tab_cell_status(self):
        """Set the table of cell status."""

        filepath = self._get_policy_dir() / "cell_geometry.yaml"

        tab_cell_status = self._control_tabs.get_tab("Cell Status")[1]
        tab_cell_status.read_cell_geometry_file(filepath)

    def _create_layout(self):
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()
        layout.addLayout(self._layout_control.layout)

        space = 20
        layout.addSpacing(space)

        layout.addLayout(self._layout_local_mode.layout)
        layout.addSpacing(space)

        layout.addLayout(self._layout_control_mode.layout)
        layout.addLayout(self._control_tabs.layout)

        return layout

    def _add_tool_bar(self):
        """Add the tool bar."""

        tool_bar = self.addToolBar("ToolBar")

        action_exit = tool_bar.addAction("Exit", self._callback_exit)
        action_exit.setToolTip("Exit the application")

        action_connect = tool_bar.addAction("Connect", self._callback_connect)
        action_connect.setToolTip("Connect to the M2 controller")

        action_disconnect = tool_bar.addAction("Disconnect", self._callback_disconnect)
        action_disconnect.setToolTip("Disconnect from the M2 controller")

        action_settings = tool_bar.addAction("Settings", self._callback_settings)
        action_settings.setToolTip("Show the application settings")

    @asyncSlot()
    async def _callback_exit(self):
        """Exit the application."""

        dialog = self._create_dialog_exit()
        result = dialog.exec()

        if result == QMessageBox.Ok:
            app = QApplication.instance()
            app.quit()

    def _create_dialog_exit(self):
        """Create the exit dialog.

        Returns
        -------
        `PySide2.QtWidgets.QMessageBox`
            Exit dialog.
        """

        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Warning)
        dialog.setWindowTitle("exit")

        if self.model.system_status["isCrioConnected"]:
            dialog.setText(
                "There is still the connection with M2 controller. Exit the application?"
            )
        else:
            dialog.setText("Exit the application?")

        dialog.addButton(QMessageBox.Cancel)
        dialog.addButton(QMessageBox.Ok)

        return dialog

    @asyncSlot()
    async def _callback_connect(self):
        """Callback function to connect to the M2 controller."""
        run_command(self.model.connect)

    @asyncSlot()
    async def _callback_disconnect(self):
        """Callback function to disconnect from the M2 controller."""
        run_command(self.model.disconnect)

    @asyncSlot()
    async def _callback_settings(self):
        """Callback function to show the settings."""
        self._tab_settings.show()

    def _set_default(self):
        """Set the default condition."""

        self._layout_control.set_csc_commander(True)
        self.model.report_config()
        self.model.utility_monitor.report_utility_status()
