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

__all__ = ["MainWindow"]

import logging
import pathlib
import sys
from datetime import datetime

from lsst.ts.m2com import read_yaml_file
from lsst.ts.tcpip import LOCAL_HOST
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QMainWindow, QToolBar, QVBoxLayout, QWidget
from qasync import QApplication, asyncSlot

from . import (
    ControlTabs,
    LogWindowHandler,
    Model,
    QMessageBoxAsync,
    SignalMessage,
    get_button_action,
    prompt_dialog_warning,
    run_command,
)
from .controltab import TabSettings
from .layout import LayoutControl, LayoutControlMode, LayoutLocalMode


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
    log_level : `int`, optional
        Logging level. (the default is `logging.WARN`)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    model : `Model`
        Model class.
    """

    def __init__(
        self,
        is_output_log_on_screen,
        is_simulation_mode,
        log=None,
        log_level=logging.WARN,
    ):
        super().__init__()

        # Signal of message
        self._signal_message = SignalMessage()

        # Set the logger
        message_format = "%(asctime)s, %(levelname)s, %(message)s"
        self.log = self._set_log(
            message_format, is_output_log_on_screen, log_level, log=log
        )

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

    def _set_log(self, message_format, is_output_log_on_screen, level, log=None):
        """Set the logger.

        Parameters
        ----------
        message_format : `str`
            Format of the message.
        is_output_log_on_screen : `bool`
            Is outputting the log messages on screen or not.
        level : `int`
            Logging level.
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

        logging.basicConfig(
            filename=self._get_log_file_name(),
            format=message_format,
        )

        log.addHandler(LogWindowHandler(self._signal_message, message_format))

        if is_output_log_on_screen:
            log.addHandler(logging.StreamHandler(sys.stdout))

        log.setLevel(level)

        return log

    def _get_log_file_name(self):
        """Get the log file name.

        Returns
        -------
        `pathlib.Path`
            Log file name.
        """

        name = "log_%s.txt" % datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        return (
            pathlib.Path(__file__).parents[0] / ".." / ".." / ".." / ".." / "log" / name
        )

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

        if is_simulation_mode:
            default_settings["host"] = LOCAL_HOST

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
        action_exit.setToolTip("Exit the application (this might take some time)")

        action_connect = tool_bar.addAction("Connect", self._callback_connect)
        action_connect.setToolTip("Connect to the M2 controller")

        action_disconnect = tool_bar.addAction("Disconnect", self._callback_disconnect)
        action_disconnect.setToolTip(
            "Disconnect and close all tasks (this might take some time)"
        )

        action_settings = tool_bar.addAction("Settings", self._callback_settings)
        action_settings.setToolTip("Show the application settings")

    @asyncSlot()
    async def _callback_exit(self):
        """Exit the application.

        The 'exit' action will be disabled during the call. If the user cancels
        the exit (in the displayed message box), it will be reenabled.
        """

        action_exit = self._get_action("Exit")
        action_exit.setEnabled(False)

        if self.model.system_status["isCrioConnected"]:
            await prompt_dialog_warning(
                "_callback_exit()",
                (
                    "M2 cRIO controller is still connected. Please disconnect "
                    "it before exiting the user interface."
                ),
            )

        else:
            dialog = self._create_dialog_exit()
            result = await dialog.show()

            if result == QMessageBoxAsync.Ok:
                # Closes the running asynchronous tasks before quitting the
                # application. This makes sure the asynchronous tasks aren't
                # running without a connection.
                if self.model.run_loops:
                    await self.model.close_tasks()

                QApplication.instance().quit()

        action_exit.setEnabled(True)

    def _get_action(self, name):
        """Get the action.

        Parameters
        ----------
        name : `str`
            Action name.

        Returns
        -------
        `PySide2.QtWidgets.QAction`
            Action.
        """

        tool_bar = self.findChildren(QToolBar)[0]
        return get_button_action(tool_bar, name)

    def _create_dialog_exit(self):
        """Create the exit dialog.

        Returns
        -------
        `QMessageBoxAsync`
            Exit dialog.
        """

        dialog = QMessageBoxAsync()
        dialog.setIcon(QMessageBoxAsync.Warning)
        dialog.setWindowTitle("exit")

        if self.model.system_status["isCrioConnected"]:
            dialog.setText("There is still the connection with M2 controller.")
        else:
            dialog.setText("Exit the application?")
            dialog.addButton(QMessageBoxAsync.Ok)

        dialog.addButton(QMessageBoxAsync.Cancel)

        # Block the user to interact with other running widgets
        dialog.setModal(True)

        return dialog

    @asyncSlot()
    async def _callback_connect(self):
        """Callback function to connect to the M2 controller.

        Disable the 'connect' action, open the connection and re-enable the
        'connect' action.
        """

        action_connect = self._get_action("Connect")
        action_connect.setEnabled(False)

        if self.model.system_status["isCrioConnected"]:
            await prompt_dialog_warning(
                "_callback_connect()", "The M2 cRIO controller is already connected."
            )
        else:
            await run_command(self.model.connect)

        action_connect.setEnabled(True)

    @asyncSlot()
    async def _callback_disconnect(self):
        """Callback function to disconnect from the M2 controller.

        The 'connect', 'disconnect' and 'exit' actions wiil be disabled before
        disconnecting and re-enabled after the controller is disconnected. That
        prevents the operator from trying to connect as asynchronous tasks are
        being closed during the disconnection command, thus preventing
        unpredictable application behavior.
        """

        action_connect = self._get_action("Connect")
        action_connect.setEnabled(False)

        action_disconnect = self._get_action("Disconnect")
        action_disconnect.setEnabled(False)

        action_exit = self._get_action("Exit")
        action_exit.setEnabled(False)

        await run_command(self.model.disconnect)

        action_connect.setEnabled(True)
        action_disconnect.setEnabled(True)
        action_exit.setEnabled(True)

    @asyncSlot()
    async def _callback_settings(self):
        """Callback function to show the settings."""
        self._tab_settings.show()

    def _set_default(self):
        """Set the default condition."""

        self.model.report_config()
        self.model.utility_monitor.report_utility_status()
