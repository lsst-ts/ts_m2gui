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

from lsst.ts.guitool import (
    ControlTabs,
    QMessageBoxAsync,
    get_button_action,
    prompt_dialog_critical,
    prompt_dialog_warning,
    run_command,
)
from lsst.ts.m2com import get_config_dir, read_yaml_file
from lsst.ts.tcpip import LOCALHOST_IPV4
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QToolBar, QVBoxLayout, QWidget
from qasync import QApplication, asyncSlot

from .controltab import (
    TabActuatorControl,
    TabAlarmWarn,
    TabCellStatus,
    TabConfigView,
    TabDetailedForce,
    TabDiagnostics,
    TabHardpointSelection,
    TabIlcStatus,
    TabNetForceMoment,
    TabOverview,
    TabRigidBodyPos,
    TabSettings,
    TabUtilityView,
)
from .layout import LayoutControl, LayoutControlMode, LayoutLocalMode
from .log_window_handler import LogWindowHandler
from .model import Model
from .signals import SignalMessage


class MainWindow(QMainWindow):
    """Main window of the application.

    Parameters
    ----------
    is_output_log_to_file : `bool`
        Is outputting the log messages to file or not.
    is_output_log_on_screen : `bool`
        Is outputting the log messages on screen or not.
    is_simulation_mode: `bool`
        Is the simulation mode or not.
    is_crio_simulator : `bool`, optional
        Is using the M2 cRIO simulator or not. (the default is False)
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
        is_output_log_to_file: bool,
        is_output_log_on_screen: bool,
        is_simulation_mode: bool,
        is_crio_simulator: bool = False,
        log: logging.Logger | None = None,
        log_level: int = logging.WARN,
    ) -> None:
        super().__init__()

        # Signal of message
        self._signal_message = SignalMessage()

        # Set the logger
        message_format = "%(asctime)s, %(levelname)s, %(message)s"
        self.log = self._set_log(
            message_format,
            is_output_log_to_file,
            is_output_log_on_screen,
            log_level,
            log=log,
        )

        self.model = self._set_model(is_simulation_mode, is_crio_simulator)

        # Layout of the control panel
        self._layout_control = LayoutControl(self.model)

        # Layout of the local mode
        self._layout_local_mode = LayoutLocalMode(self.model)

        # Layout of the control mode
        self._layout_control_mode = LayoutControlMode(self.model)

        # Control tables
        tabs = [
            TabOverview("Overview", self.model),
            TabActuatorControl("Actuator Control", self.model),
            TabConfigView("Configuration View", self.model),
            TabCellStatus("Cell Status", self.model),
            TabUtilityView("Utility View", self.model),
            TabRigidBodyPos("Rigid Body Position", self.model),
            TabDetailedForce("Detailed Force", self.model),
            TabDiagnostics("Diagnostics", self.model),
            TabAlarmWarn("Alarms/Warnings", self.model),
            TabIlcStatus("ILC Status", self.model),
            TabNetForceMoment("Net Force/Moment", self.model),
            TabHardpointSelection("Hardpoints", self.model),
        ]
        self._control_tabs = ControlTabs(tabs)
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
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self._add_tool_bar()

        self._set_default()

        if is_simulation_mode:
            self.log.info("Running the simulation mode.")

        if is_crio_simulator:
            self.log.info("Using the M2 cRIO simulator.")

    def _set_log(
        self,
        message_format: str,
        is_output_log_to_file: bool,
        is_output_log_on_screen: bool,
        level: int,
        log: logging.Logger | None = None,
    ) -> logging.Logger:
        """Set the logger.

        Parameters
        ----------
        message_format : `str`
            Format of the message.
        is_output_log_to_file : `bool`
            Is outputting the log messages to file or not.
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

        if is_output_log_to_file:
            logging.basicConfig(
                filename=self._get_log_file_name(),
                format=message_format,
            )
        else:
            logging.basicConfig(
                format=message_format,
            )

        log.addHandler(LogWindowHandler(self._signal_message, message_format))

        if is_output_log_on_screen:
            log.addHandler(logging.StreamHandler(sys.stdout))

        log.setLevel(level)

        return log

    def _get_log_file_name(self, default_log_dir: str = "/rubin/mtm2/log") -> pathlib.Path:
        """Get the log file name.

        Parameters
        ----------
        default_log_dir : `str`, optional
            Default log directory. (the default is "/rubin/mtm2/log")

        Returns
        -------
        `pathlib.Path`
            Log file name.
        """

        log_dir = pathlib.Path(default_log_dir)
        if not log_dir.is_dir():
            print(
                (f"Default log directory: {default_log_dir} does not exist. Use the home directory instead.")
            )
            log_dir = pathlib.Path.home()

        name = "log_%s.txt" % datetime.now().strftime("%d_%m_%Y_%H_%M_%S")

        return log_dir / name

    def _set_model(self, is_simulation_mode: bool, is_crio_simulator: bool) -> Model:
        """Set the model.

        Parameters
        ----------
        is_simulation_mode: `bool`
            Is the simulation mode or not.
        is_crio_simulator : `bool`
            Is using the M2 cRIO simulator or not.

        Returns
        -------
        model : `Model`
            Model object.

        Raises
        ------
        `ValueError`
            When simulation mode and cRIO simulator are used.
        """

        if is_simulation_mode and is_crio_simulator:
            raise ValueError("No simulation mode and cRIO simulator at the same time.")

        # Read the yaml file
        filepath = get_config_dir() / "default_gui.yaml"
        default_settings = read_yaml_file(filepath)

        if is_simulation_mode:
            default_settings["host"] = LOCALHOST_IPV4
        elif is_crio_simulator:
            default_settings["host"] = default_settings["host_crio_simulator"]

        model = Model(
            self.log,
            host=default_settings["host"],
            port_command=default_settings["port_command"],
            port_telemetry=default_settings["port_telemetry"],
            timeout_connection=default_settings["timeout_connection"],
            is_simulation_mode=is_simulation_mode,
        )

        return model

    def _set_control_tabs(self) -> None:
        """Set the control tables"""

        self._set_tab_overview()
        self._set_tab_alarm_warn()
        self._set_tab_cell_status()
        self._set_tab_ilc_status()
        self._set_tab_hardpoint_selection()

    def _set_tab_overview(self) -> None:
        """Set the table of overview."""

        tab_overview = self._control_tabs.get_tab("Overview")[1]

        # Workaround of the mypy checking
        assert tab_overview is not None

        tab_overview.set_signal_control(self.model.signal_control)
        tab_overview.set_signal_message(self._signal_message)

    def _set_tab_alarm_warn(self) -> None:
        """Set the table of alarms and warnings."""

        filepath = get_config_dir() / "error_code.tsv"

        tab_alarm_warn = self._control_tabs.get_tab("Alarms/Warnings")[1]

        # Workaround of the mypy checking
        assert tab_alarm_warn is not None

        tab_alarm_warn.read_error_list_file(filepath)

    def _set_tab_cell_status(self) -> None:
        """Set the table of cell status."""

        filepath = get_config_dir() / "harrisLUT" / "cell_geom.yaml"

        tab_cell_status = self._control_tabs.get_tab("Cell Status")[1]

        # Workaround of the mypy checking
        assert tab_cell_status is not None

        tab_cell_status.read_cell_geometry_file(filepath)

    def _set_tab_ilc_status(self) -> None:
        """Set the table of inner-loop controller (ILC) status."""

        filepath = get_config_dir() / "ilc_details.yaml"

        tab_ilc_status = self._control_tabs.get_tab("ILC Status")[1]

        # Workaround of the mypy checking
        assert tab_ilc_status is not None

        tab_ilc_status.read_ilc_details_file(filepath)

    def _set_tab_hardpoint_selection(self) -> None:
        """Set the table of hardpoint selection."""

        filepath = get_config_dir() / "harrisLUT" / "cell_geom.yaml"

        tab_hardpoint_selection = self._control_tabs.get_tab("Hardpoints")[1]

        # Workaround of the mypy checking
        assert tab_hardpoint_selection is not None

        tab_hardpoint_selection.read_cell_geometry_file(filepath)

    def _create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
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

    def _add_tool_bar(self) -> None:
        """Add the tool bar."""

        tool_bar = self.addToolBar("ToolBar")

        action_exit = tool_bar.addAction("Exit", self._callback_exit)
        action_exit.setToolTip("Exit the application (this might take some time)")

        action_connect = tool_bar.addAction("Connect", self._callback_connect)
        action_connect.setToolTip("Connect to the M2 controller")

        action_disconnect = tool_bar.addAction("Disconnect", self._callback_disconnect)
        action_disconnect.setToolTip("Disconnect and close all tasks (this might take some time)")

        action_settings = tool_bar.addAction("Settings", self._callback_settings)
        action_settings.setToolTip("Show the application settings")

    @asyncSlot()
    async def _callback_exit(self) -> None:
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
                await self.model.controller.close_controller_and_mock_server()

                QApplication.instance().quit()

        action_exit.setEnabled(True)

    def _get_action(self, name: str) -> QAction:
        """Get the action.

        Parameters
        ----------
        name : `str`
            Action name.

        Returns
        -------
        `PySide6.QtWidgets.QAction`
            Action.
        """

        tool_bar = self.findChildren(QToolBar)[0]
        return get_button_action(tool_bar, name)

    def _create_dialog_exit(self) -> QMessageBoxAsync:
        """Create the exit dialog.

        Returns
        -------
        dialog : `QMessageBoxAsync`
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
    async def _callback_connect(self) -> None:
        """Callback function to connect to the M2 controller.

        Disable the 'connect' action, open the connection and re-enable the
        'connect' action.
        """

        action_connect = self._get_action("Connect")
        action_connect.setEnabled(False)

        if self.model.system_status["isCrioConnected"]:
            await prompt_dialog_warning("_callback_connect()", "The M2 cRIO controller is already connected.")
        else:
            try:
                await run_command(self.model.connect)
            except Exception as ex:
                await prompt_dialog_critical(
                    "_callback_connect",
                    f"Cannot connect to LabVIEW remote - {ex}",
                )

        action_connect.setEnabled(True)

    @asyncSlot()
    async def _callback_disconnect(self) -> None:
        """Callback function to disconnect from the M2 controller.

        The 'connect', 'disconnect' and 'exit' actions wiil be disabled before
        disconnecting and re-enabled after the controller is disconnected. That
        prevents the operator from trying to connect as asynchronous tasks are
        being closed during the disconnection command, thus preventing
        unpredictable application behavior.
        """

        # If the commander is not CSC, notify the user.
        if self.model.system_status["isCrioConnected"] and (not self.model.is_csc_commander):
            dialog = self._create_dialog_disconnect()
            result = await dialog.show()

            if result == QMessageBoxAsync.Cancel:
                return

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

    def _create_dialog_disconnect(self) -> QMessageBoxAsync:
        """Create the disconnect dialog.

        Returns
        -------
        dialog : `QMessageBoxAsync`
            Disconnect dialog.
        """

        dialog = QMessageBoxAsync()
        dialog.setIcon(QMessageBoxAsync.Warning)
        dialog.setWindowTitle("disconnect")

        dialog.setText(
            "The current commander is GUI. Please consider to switch to CSC "
            "before the disconnection.\n\n"
            "Do you want to continue the disconnection?"
        )

        dialog.addButton(QMessageBoxAsync.Ok)
        dialog.addButton(QMessageBoxAsync.Cancel)

        # Block the user to interact with other running widgets
        dialog.setModal(True)

        return dialog

    @asyncSlot()
    async def _callback_settings(self) -> None:
        """Callback function to show the settings."""
        self._tab_settings.show()

    def _set_default(self) -> None:
        """Set the default condition."""

        self.model.report_config()
        self.model.utility_monitor.report_utility_status()
