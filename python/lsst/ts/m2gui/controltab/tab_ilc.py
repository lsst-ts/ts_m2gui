# This file is part of ts_m2gui.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

__all__ = ["TabIlc"]

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from lsst.ts.guitool import (
    create_double_spin_box,
    create_group_box,
    create_label,
    create_radio_indicators,
    run_command,
    set_button,
    update_boolean_indicator_status,
)
from lsst.ts.m2com import NUM_ACTUATOR
from lsst.ts.xml.enums import MTM2

from ..model import Model
from ..utils import is_closed_loop_control_mode_in_idle
from .tab_default import TabDefault


class TabIlc(TabDefault):
    """Table of the inner-loop controller (ILC).

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.
    one_based_address : `int`
        One-based address of the ILC.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    NUM_CHANNEL = 4

    def __init__(self, title: str, model: Model, one_based_address: int) -> None:
        super().__init__(title, model)

        self._one_based_address = one_based_address

        self._labels = self._create_labels()

        # 16 bits
        self._list_status_word = {
            "status": create_radio_indicators(16),
            "faults": create_radio_indicators(16),
        }

        self._command_parameters = self._create_command_parameters()
        self._commands = self._create_commands()

        self._button_command = set_button(
            "Send Command",
            self._callback_send_command,
            tool_tip="Send the command to the controller.",
        )

        self.set_widget_and_layout()

        self._set_default()

    def _create_labels(self) -> dict[str, QLabel]:
        """Create the labels.

        Returns
        -------
        labels : `dict` [`str`, `PySide6.QtWidgets.QLabel`]
            Labels.
        """

        names = [
            "unique_id",
            "application_type",
            "network_node_type",
            "selected_options",
            "network_node_options",
            "firmware_revision",
            "firmware_name",
            "mode",
            "status",
            "faults",
            "rate",
            "main_gain_1",
            "main_gain_2",
            "main_gain_3",
            "main_gain_4",
            "main_offset_1",
            "main_offset_2",
            "main_offset_3",
            "main_offset_4",
            "main_sensitivity_1",
            "main_sensitivity_2",
            "main_sensitivity_3",
            "main_sensitivity_4",
            "backup_gain_1",
            "backup_gain_2",
            "backup_gain_3",
            "backup_gain_4",
            "backup_offset_1",
            "backup_offset_2",
            "backup_offset_3",
            "backup_offset_4",
            "backup_sensitivity_1",
            "backup_sensitivity_2",
            "backup_sensitivity_3",
            "backup_sensitivity_4",
        ]

        labels = dict()
        for name in names:
            labels[name] = create_label("")

        return labels

    def _create_command_parameters(
        self,
        decimal_calibration: int = 5,
    ) -> dict:
        """Create the command parameters.

        Parameters
        ----------
        decimal_calibration : `int`, optional
            Decimal of the calibration data. (the default is 5)

        Returns
        -------
        `dict`
            Command parameters.
        """

        allowed_modes = (
            [
                MTM2.InnerLoopControlMode.Standby,
                MTM2.InnerLoopControlMode.Disabled,
                MTM2.InnerLoopControlMode.Enabled,
                MTM2.InnerLoopControlMode.FirmwareUpdate,
                MTM2.InnerLoopControlMode.Fault,
                MTM2.InnerLoopControlMode.ClearFaults,
                MTM2.InnerLoopControlMode.NoChange,
            ]
            if self.is_actuator_ilc()
            else [
                MTM2.InnerLoopControlMode.Standby,
                MTM2.InnerLoopControlMode.Enabled,
                MTM2.InnerLoopControlMode.FirmwareUpdate,
                MTM2.InnerLoopControlMode.Fault,
                MTM2.InnerLoopControlMode.ClearFaults,
                MTM2.InnerLoopControlMode.NoChange,
            ]
        )

        mode = QComboBox()
        for allowed_mode in allowed_modes:
            mode.addItem(allowed_mode.name)

        rate = create_double_spin_box(
            "",
            0,
            maximum=12,
        )

        channel = create_double_spin_box(
            "",
            0,
            maximum=4,
            minimum=1,
        )
        channel.valueChanged.connect(self._callback_channel_value_changed)

        limit_offset = 100.0
        offset = create_double_spin_box(
            "",
            decimal_calibration,
            maximum=limit_offset,
            minimum=-limit_offset,
        )

        sensitivity = create_double_spin_box(
            "",
            decimal_calibration,
            maximum=10.0,
        )

        return {
            "mode": mode,
            "rate": rate,
            "channel": channel,
            "offset": offset,
            "sensitivity": sensitivity,
        }

    @asyncSlot()
    async def _callback_channel_value_changed(self) -> None:
        """Callback of the channel value changed. Update the offset and
        sensitivity based on the selected channel."""

        self._update_offset_and_sensitivity_based_on_channel()

    def _update_offset_and_sensitivity_based_on_channel(self) -> None:
        """Update the offset and sensitivity based on the selected channel."""

        channel = int(self._command_parameters["channel"].value())
        offset = float(self._labels[f"main_offset_{channel}"].text())
        sensitivity = float(self._labels[f"main_sensitivity_{channel}"].text())

        self._command_parameters["offset"].setValue(offset)
        self._command_parameters["sensitivity"].setValue(sensitivity)

    def is_actuator_ilc(self) -> bool:
        """Is the actuator inner-loop controller (ILC) or not.

        Returns
        -------
        `bool`
            True if the ILC is actuator, False otherwise.
        """

        return self._one_based_address <= NUM_ACTUATOR

    def _create_commands(self) -> dict:
        """Create the commands.

        Returns
        -------
        `dict`
            Commands. The key is the name of the command and the value is the
            button.
        """

        command_set_mode = QRadioButton("Set Mode Command", parent=self)
        command_report_server_id = QRadioButton("Report Server ID Command", parent=self)
        command_report_server_status = QRadioButton("Report Server Status Command", parent=self)
        command_reset = QRadioButton("Reset Command", parent=self)
        command_read_calibration_data = QRadioButton("Read Calibration Data Command", parent=self)
        command_get_scan_rate = QRadioButton("Get Scan Rate Command", parent=self)
        command_set_scan_rate = QRadioButton("Set Scan Rate Command", parent=self)
        command_set_offset_and_sensitivity = QRadioButton("Set Offset and Sensitivity Command", parent=self)

        command_set_offset_and_sensitivity.setToolTip(
            "After sending this command, needs to reset\nthe ILC or power-cycle the communication."
        )

        command_set_mode.toggled.connect(self._callback_command)
        command_report_server_id.toggled.connect(self._callback_command)
        command_report_server_status.toggled.connect(self._callback_command)
        command_reset.toggled.connect(self._callback_command)
        command_read_calibration_data.toggled.connect(self._callback_command)
        command_get_scan_rate.toggled.connect(self._callback_command)
        command_set_scan_rate.toggled.connect(self._callback_command)
        command_set_offset_and_sensitivity.toggled.connect(self._callback_command)

        return {
            "set_mode": command_set_mode,
            "server_id": command_report_server_id,
            "server_status": command_report_server_status,
            "reset": command_reset,
            "calibration_data": command_read_calibration_data,
            "get_rate": command_get_scan_rate,
            "set_rate": command_set_scan_rate,
            "set_offset_and_sensitivity": command_set_offset_and_sensitivity,
        }

    @asyncSlot()
    async def _callback_command(self) -> None:
        """Callback of the command button."""

        if self._commands["set_mode"].isChecked():
            self._enable_command_parameters(["mode"])

        elif self._commands["server_id"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["server_status"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["reset"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["calibration_data"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["get_rate"].isChecked():
            self._enable_command_parameters([])

        elif self._commands["set_rate"].isChecked():
            self._enable_command_parameters(["rate"])

        elif self._commands["set_offset_and_sensitivity"].isChecked():
            self._enable_command_parameters(["channel", "offset", "sensitivity"])

        self._update_offset_and_sensitivity_based_on_channel()

    def _enable_command_parameters(self, enabled_parameters: list[str]) -> None:
        """Enable the command parameters.

        Parameters
        ----------
        enabled_parameters : `list` [`str`]
            Enabled command parameters.
        """

        for name, value in self._command_parameters.items():
            value.setEnabled(name in enabled_parameters)

    @asyncSlot()
    async def _callback_send_command(self) -> None:
        """Callback of the send-command button to command the controller."""

        # If the closed-loop control mode is not in Idle, return immediately.
        is_idle = await is_closed_loop_control_mode_in_idle(
            self.model.controller.closed_loop_control_mode,
            "_callback_send_command()",
        )
        if not is_idle:
            return

        # Check the selected command
        name = self._get_selected_command()

        self.model.log.info(f"Send the ILC command: {name}.")

        # Command the controller
        zero_based_address = self._one_based_address - 1
        match name:
            case "set_mode":
                mode_command = self._get_mode()
                if mode_command != MTM2.InnerLoopControlMode.Unknown:
                    await run_command(
                        self.model.controller.set_single_ilc_mode,
                        zero_based_address,
                        mode_command,
                    )

            case "server_id":
                await run_command(
                    self.model.controller.report_server_id,
                    zero_based_address,
                )

            case "server_status":
                await run_command(
                    self.model.controller.report_server_status,
                    zero_based_address,
                )

            case "reset":
                await run_command(
                    self.model.controller.reset_inner_loop_controller,
                    zero_based_address,
                )

            case "calibration_data":
                await run_command(
                    self.model.controller.read_calibration_data,
                    zero_based_address,
                )

            case "get_rate":
                await run_command(
                    self.model.controller.get_scan_rate,
                    zero_based_address,
                )

            case "set_rate":
                rate = int(self._command_parameters["rate"].value())
                await run_command(
                    self.model.controller.set_scan_rate,
                    zero_based_address,
                    rate,
                )

            case "set_offset_and_sensitivity":
                zero_based_channel, offset, sensitivity = self._get_zero_based_channel_offset_sensitivity()
                await run_command(
                    self.model.controller.set_offset_and_sensitivity,
                    zero_based_address,
                    zero_based_channel,
                    offset,
                    sensitivity,
                )

            case _:
                # Should not reach here
                self.model.log.error(f"Unknown command: {name}.")

    def _get_mode(self) -> MTM2.InnerLoopControlMode:
        """Get the selected mode.

        Returns
        -------
        enum `MTM2.InnerLoopControlMode`
            Selected mode.
        """

        mode = self._command_parameters["mode"].currentText()
        try:
            return MTM2.InnerLoopControlMode[mode]

        except KeyError:
            self.model.log.error(f"Unknown mode: {mode}.")
            return MTM2.InnerLoopControlMode.Unknown

    def _get_zero_based_channel_offset_sensitivity(self) -> tuple[int, float, float]:
        """Get the selected 0-based channel, offset, and sensitivity.

        Returns
        -------
        `int`
            Zero-based channel.
        `float`
            Offset.
        `float`
            Sensitivity.
        """

        return (
            int(self._command_parameters["channel"].value()) - 1,
            self._command_parameters["offset"].value(),
            self._command_parameters["sensitivity"].value(),
        )

    def _get_selected_command(self) -> str:
        """Get the selected command.

        Returns
        -------
        name : `str`
            Selected command.
        """

        for name, commmand in self._commands.items():
            if commmand.isChecked():
                return name

        return ""

    def create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout.
        """

        # First column
        layout_server = QVBoxLayout()
        layout_server.addWidget(self._create_group_server_id())
        layout_server.addWidget(self._create_group_server_status())

        if self.is_actuator_ilc():
            layout_server.addWidget(self._create_group_server_rate())

        # Second column
        layout_calibration_data = QVBoxLayout()
        if self.is_actuator_ilc():
            layout_calibration_data.addWidget(self._create_group_calibration_data("Main"))
            layout_calibration_data.addWidget(self._create_group_calibration_data("Backup"))

        # Third column
        layout_status = QVBoxLayout()
        layout_status.addWidget(self._create_group_status())

        # Fourth column
        layout_faults = QVBoxLayout()
        layout_faults.addWidget(self._create_group_faults())

        # Fifth column
        layout_command = QVBoxLayout()
        layout_command.addWidget(self._create_group_command_name())
        layout_command.addWidget(self._create_group_command_parameters())

        # Add the layouts to the main layout
        layout = QHBoxLayout()
        layout.addLayout(layout_server)

        if self.is_actuator_ilc():
            layout.addLayout(layout_calibration_data)

        layout.addLayout(layout_status)
        layout.addLayout(layout_faults)
        layout.addLayout(layout_command)

        return layout

    def _create_group_server_id(self) -> QGroupBox:
        """Create the group of server identifier.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Unique Id:", self._labels["unique_id"])
        layout.addRow("Application Type:", self._labels["application_type"])
        layout.addRow("Network Node Type:", self._labels["network_node_type"])
        layout.addRow("Selected Options:", self._labels["selected_options"])
        layout.addRow("Network Node Options:", self._labels["network_node_options"])
        layout.addRow("Firmware Revision:", self._labels["firmware_revision"])
        layout.addRow("Firmware Name:", self._labels["firmware_name"])

        return create_group_box("Server Identifier", layout)

    def _create_group_server_status(self) -> QGroupBox:
        """Create the group of server status.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Mode:", self._labels["mode"])
        layout.addRow("Status:", self._labels["status"])
        layout.addRow("Faults:", self._labels["faults"])

        return create_group_box("Server Status", layout)

    def _create_group_server_rate(self) -> QGroupBox:
        """Create the group of server ADC scan rate.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Scan Rate:", self._labels["rate"])

        return create_group_box("Rate", layout)

    def _create_group_calibration_data(self, prefix: str) -> QGroupBox:
        """Create the group of calibration data.

        Parameters
        ----------
        prefix : `str`
            Prefix of name.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        names = ["Gain", "Offset", "Sensitivity"]

        layout = QFormLayout()
        for idx_name, name in enumerate(names):
            for idx_channel in range(1, self.NUM_CHANNEL + 1):
                layout.addRow(
                    f"{name} {idx_channel}:", self._labels[f"{prefix.lower()}_{name.lower()}_{idx_channel}"]
                )

            if idx_name < (len(names) - 1):
                self.add_empty_row_to_form_layout(layout)

        return create_group_box(f"{prefix} Calibration Data", layout)

    def _create_group_status(self) -> QGroupBox:
        """Create the group of status.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        names = [
            "Bit 0 - Major Fault:",
            "Bit 1 - Minor Fault:",
            "Bit 2 - Reserved:",
            "Bit 3 - Fault Override:",
            "Bit 4 - Main Calibration Error:",
            "Bit 5 - Backup Calibration Error:",
            "Bit 6 - Reserved:",
            "Bit 7 - Reserved:",
            "Bit 8 - Limit Switch 1 Activated:",
            "Bit 9 - Limit Switch 2 Activated:",
            "Bit 10 - Reserved:",
            "Bit 11 - Reserved:",
            "Bit 12 - Monitor Instrument Timeout:",
            "Bit 13 - Reserved:",
            "Bit 14 - Reserved:",
            "Bit 15 - Reserved:",
        ]

        return create_group_box(
            "Status",
            self._create_form_layout(
                names,
                self._list_status_word["status"],
            ),
        )

    def _create_form_layout(self, names: list[str], items: list[QRadioButton]) -> QFormLayout:
        """Create a form layout.

        Parameters
        ----------
        names : `list` [`str`]
            Names.
        items : `list` [`QRadioButton`]
            Items.

        Returns
        -------
        layout : `QFormLayout`
            Form layout.
        """

        layout = QFormLayout()
        for name, item in zip(names, items):
            layout.addRow(name, item)

        return layout

    def _create_group_faults(self) -> QGroupBox:
        """Create the group of faults.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        names = [
            "Bit 0 - Unique ID Error:",
            "Bit 1 - App/Network Type Dismatch:",
            "Bit 2 - No App Programmed:",
            "Bit 3 - App CRC Error:",
            "Bit 4 - No 1-Wire Found:",
            "Bit 5 - 1-Wire Copy 1 Error:",
            "Bit 6 - 1-Wire Copy 2 Error:",
            "Bit 7 - Reserved:",
            "Bit 8 - Watchdog Reset (Timeout):",
            "Bit 9 - Power Brown-Out Occurred:",
            "Bit 10 - Event Trap Occurred:",
            "Bit 11 - Motor Driver Fail:",
            "Bit 12 - SSR Power Fail:",
            "Bit 13 - Aux Power Fail:",
            "Bit 14 - Motor Controller Power Fail:",
            "Bit 15 - Reserved:",
        ]

        return create_group_box(
            "Faults",
            self._create_form_layout(
                names,
                self._list_status_word["faults"],
            ),
        )

    def _create_group_command_name(self) -> QGroupBox:
        """Create the group of command name.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()
        for idx, command in enumerate(self._commands.values()):
            layout.addWidget(command)

        if not self.is_actuator_ilc():
            for name in ["calibration_data", "get_rate", "set_rate", "set_offset_and_sensitivity"]:
                self._commands[name].setEnabled(False)

        layout.addWidget(self._button_command)

        return create_group_box("Command", layout)

    def _create_group_command_parameters(self) -> QGroupBox:
        """Create the group of command parameters.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Mode:", self._command_parameters["mode"])
        layout.addRow("Scan Rate:", self._command_parameters["rate"])
        layout.addRow("Channel:", self._command_parameters["channel"])
        layout.addRow("Offset:", self._command_parameters["offset"])
        layout.addRow("Sensitivity:", self._command_parameters["sensitivity"])

        return create_group_box("Command Parameters", layout)

    def _set_default(self) -> None:
        """Set the default values to the labels and radio indicators."""

        self.set_server_id(0, 0, 0, 0, 0, "0.0", "Unknown")
        self.set_server_status(MTM2.InnerLoopControlMode.Unknown, status=0, faults=0)
        self.set_scan_rate(-1)

        self.set_calibration_data(
            [0.0] * self.NUM_CHANNEL,
            [0.0] * self.NUM_CHANNEL,
            [0.0] * self.NUM_CHANNEL,
            [0.0] * self.NUM_CHANNEL,
            [0.0] * self.NUM_CHANNEL,
            [0.0] * self.NUM_CHANNEL,
        )

        self._commands["set_mode"].setChecked(True)

    def set_server_id(
        self,
        unique_id: int,
        application_type: int,
        network_node_type: int,
        selected_options: int,
        network_node_options: int,
        firmware_revision: str,
        firmware_name: str,
    ) -> None:
        """Set the server identifier.

        Parameters
        ----------
        unique_id : `int`
            Unique identifier.
        application_type : `int`
            Application type.
        network_node_type : `int`
            Network node type.
        selected_options : `int`
            Selected options.
        network_node_options : `int`
            Network node options.
        firmware_revision : `str`
            Firmware revision.
        firmware_name : `str`
            Firmware name.
        """

        self._labels["unique_id"].setText(str(unique_id))
        self._labels["network_node_type"].setText(str(network_node_type))
        self._labels["selected_options"].setText(str(selected_options))
        self._labels["network_node_options"].setText(str(network_node_options))
        self._labels["firmware_revision"].setText(firmware_revision)
        self._labels["firmware_name"].setText(firmware_name)

        match application_type:
            case 1:
                self._labels["application_type"].setText("Electrical Actuator (1)")

            case 4:
                self._labels["application_type"].setText("Temperature Monitor (4)")

            case 5:
                self._labels["application_type"].setText("Displacement Monitor (5)")

            case 6:
                self._labels["application_type"].setText("Inclinometer Monitor (6)")

            case 10:
                self._labels["application_type"].setText("Bootloader (10)")

            case _:
                self._labels["application_type"].setText(f"Unknown ({application_type})")

    def set_server_status(
        self,
        mode: MTM2.InnerLoopControlMode,
        status: int | None = None,
        faults: int | None = None,
    ) -> None:
        """Set the server status.

        Parameters
        ----------
        mode : enum `MTM2.InnerLoopControlMode`
            Inner loop controller (ILC) mode.
        status : `int` or None, optional
            Status (the default is None).
        faults : `int` or None, optional
            Faults (the default is None).
        """

        self._labels["mode"].setText(mode.name)

        if status is not None:
            self._labels["status"].setText(hex(status))
            self._update_boolean_indicators(
                status,
                self._list_status_word["status"],
            )

        if faults is not None:
            self._labels["faults"].setText(hex(faults))
            self._update_boolean_indicators(
                faults,
                self._list_status_word["faults"],
            )

    def _update_boolean_indicators(
        self,
        status: int,
        indicators: list[QRadioButton],
    ) -> None:
        """Update the boolean indicators.

        Parameters
        ----------
        status : `int`
            Status.
        indicators : `list` [`QRadioButton`]
            Indicators.
        """

        for idx, indicator in enumerate(indicators):
            is_bit_on = status & (1 << idx)
            update_boolean_indicator_status(
                indicator,
                is_bit_on,
                is_fault=True,
            )

    def set_scan_rate(self, rate: int) -> None:
        """Set the ADC scan rate.

        Parameters
        ----------
        rate : `int`
            Scan rate.
        """

        match rate:
            case 0:
                self._labels["rate"].setText("50 (0)")
            case 1:
                self._labels["rate"].setText("60 (1)")
            case 2:
                self._labels["rate"].setText("100 (2)")
            case 3:
                self._labels["rate"].setText("120 (3)")
            case 4:
                self._labels["rate"].setText("200 (4)")
            case 5:
                self._labels["rate"].setText("240 (5)")
            case 6:
                self._labels["rate"].setText("300 (6)")
            case 7:
                self._labels["rate"].setText("400 (7)")
            case 8:
                self._labels["rate"].setText("480 (8)")
            case 9:
                self._labels["rate"].setText("600 (9)")
            case 10:
                self._labels["rate"].setText("1200 (10)")
            case 11:
                self._labels["rate"].setText("2400 (11)")
            case 12:
                self._labels["rate"].setText("4800 (12)")
            case _:
                self._labels["rate"].setText(f"Unknown ({rate})")

    def set_calibration_data(
        self,
        main_gains: list[float],
        main_offsets: list[float],
        main_sensitivities: list[float],
        backup_gains: list[float],
        backup_offsets: list[float],
        backup_sensitivities: list[float],
    ) -> None:
        """Set the calibration data.

        Parameters
        ----------
        main_gains : `list` [`float`]
            Main gains.
        main_offsets : `list` [`float`]
            Main offsets.
        main_sensitivities : `list` [`float`]
            Main sensitivities.
        backup_gains : `list` [`float`]
            Backup gains.
        backup_offsets : `list` [`float`]
            Backup offsets.
        backup_sensitivities : `list` [`float`]
            Backup sensitivities.
        """

        for idx, gain in enumerate(main_gains):
            self._labels[f"main_gain_{idx + 1}"].setText(f"{gain:.6e}")

        for idx, offset in enumerate(main_offsets):
            self._labels[f"main_offset_{idx + 1}"].setText(f"{offset:.5f}")

        for idx, sensitivity in enumerate(main_sensitivities):
            self._labels[f"main_sensitivity_{idx + 1}"].setText(f"{sensitivity:.5f}")

        for idx, gain in enumerate(backup_gains):
            self._labels[f"backup_gain_{idx + 1}"].setText(f"{gain:.6e}")

        for idx, offset in enumerate(backup_offsets):
            self._labels[f"backup_offset_{idx + 1}"].setText(f"{offset:.5f}")

        for idx, sensitivity in enumerate(backup_sensitivities):
            self._labels[f"backup_sensitivity_{idx + 1}"].setText(f"{sensitivity:.5f}")
