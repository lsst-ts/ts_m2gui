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

__all__ = ["TabDiagnostics"]

from lsst.ts.guitool import (
    ButtonStatus,
    QMessageBoxAsync,
    create_group_box,
    create_label,
    prompt_dialog_warning,
    run_command,
    set_button,
    update_button_color,
)
from lsst.ts.m2com import (
    TANGENT_LINK_LOAD_BEARING_LINK,
    TANGENT_LINK_NON_LOAD_BEARING_LINK,
    TANGENT_LINK_THETA_Z_MOMENT,
    TANGENT_LINK_TOTAL_WEIGHT_ERROR,
    DigitalOutputStatus,
)
from lsst.ts.xml.enums import MTM2
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..enums import LocalMode
from ..force_error_tangent import ForceErrorTangent
from ..model import Model
from ..signals import SignalClosedLoopControlMode, SignalDetailedForce, SignalUtility
from .tab_default import TabDefault


class TabDiagnostics(TabDefault):
    """Table of the diagnostics.

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    # Colors used in the label's text
    COLOR_BLACK = Qt.black.name
    COLOR_RED = Qt.red.name

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        # Utility data
        self._power_calibrated = self._create_labels_power()
        self._power_raw = self._create_labels_power()

        self._force_error_tangent = {
            "a1": create_label(tool_tip=f"Threshold is {TANGENT_LINK_NON_LOAD_BEARING_LINK} N"),
            "a2": create_label(tool_tip=f"Threshold is {TANGENT_LINK_LOAD_BEARING_LINK} N"),
            "a3": create_label(tool_tip=f"Threshold is {TANGENT_LINK_LOAD_BEARING_LINK} N"),
            "a4": create_label(tool_tip=f"Threshold is {TANGENT_LINK_NON_LOAD_BEARING_LINK} N"),
            "a5": create_label(tool_tip=f"Threshold is {TANGENT_LINK_LOAD_BEARING_LINK} N"),
            "a6": create_label(tool_tip=f"Threshold is {TANGENT_LINK_LOAD_BEARING_LINK} N"),
            "total_weight": create_label(tool_tip=f"Threshold is {TANGENT_LINK_TOTAL_WEIGHT_ERROR} N"),
            "tangent_sum": create_label(tool_tip=f"Threshold is {TANGENT_LINK_THETA_Z_MOMENT} N"),
        }

        self._button_reboot = set_button("Reboot Controller", self._callback_reboot_controller)

        self._button_update_control_mode = set_button(
            "Update Control Mode",
            self._callback_update_control_mode,
            tool_tip="Update the closed-loop control mode.",
        )
        self._control_mode_selection = self._create_control_mode_selection()

        self._digital_status_input = self._create_indicators_digital_status(
            self._get_list_digital_status_input()
        )
        self._digital_status_output = self._create_indicators_digital_status(
            self._get_list_digital_status_output()
        )

        self._digital_status_control = self._create_controls_digital_status(
            len(self._get_list_digital_status_output())
        )

        self.set_widget_and_layout(is_scrollable=True)

        self._set_signal_utility(self.model.utility_monitor.signal_utility)
        self._set_signal_detailed_force(self.model.utility_monitor.signal_detailed_force)
        self._set_signal_closed_loop_control_mode(self.model.signal_closed_loop_control_mode)

    def _create_labels_power(self) -> dict[str, QLabel]:
        """Create the labels of power.

        Returns
        -------
        `dict [PySide6.QtWidgets.QLabel]`
            Labels of the power. The key is the specific power's name.
        """

        return {
            "power_voltage_motor": create_label(),
            "power_current_motor": create_label(),
            "power_voltage_communication": create_label(),
            "power_current_communication": create_label(),
        }

    @asyncSlot()
    async def _callback_reboot_controller(self) -> None:
        """Callback of the reboot-cell-controller button. This will ask the
        user to confirm this command again."""

        dialog = QMessageBoxAsync()

        dialog.setText("This will reboot the cell controller.")
        dialog.setInformativeText("Are you sure to reboot the controller?")

        dialog.setStandardButtons(QMessageBoxAsync.Ok | QMessageBoxAsync.Cancel)
        dialog.setDefaultButton(QMessageBoxAsync.Cancel)

        # Make dialog modal, disallow interaction with other running widgets
        dialog.setModal(True)

        decision = await dialog.show()
        if decision == QMessageBoxAsync.Ok:
            await run_command(self.model.reboot_controller)

    @asyncSlot()
    async def _callback_update_control_mode(self) -> None:
        """Callback of the update-control-mode button. This will update the
        closed-loop control mode in cell."""

        # Index begins from 0 instead of 1 in QComboBox
        mode = MTM2.ClosedLoopControlMode(self._control_mode_selection.currentIndex() + 1)
        await run_command(
            self.model.controller.set_closed_loop_control_mode,
            mode,
            timeout=20.0,  # type: ignore[arg-type]
        )

    def _create_control_mode_selection(self) -> QComboBox:
        """Create the combo box of closed-loop control mode selection.

        Returns
        -------
        `PySide6.QtWidgets.QComboBox`
            Closed-loop control mode selection.
        """

        mode_selection = QComboBox()

        for mode in MTM2.ClosedLoopControlMode:
            mode_selection.addItem(mode.name)

        return self._update_index_control_mode_selection(mode_selection)

    def _update_index_control_mode_selection(self, mode_selection: QComboBox) -> QComboBox:
        """Update the index of closed-loop control mode selection.

        Parameters
        ----------
        mode_selection : `PySide6.QtWidgets.QComboBox`
            Closed-loop control mode selection.

        Returns
        -------
        mode_selection : `PySide6.QtWidgets.QComboBox`
            Updated closed-loop control mode selection.
        """

        # Index begins from 0 instead of 1 in QComboBox
        index = self.model.controller.closed_loop_control_mode.value - 1
        mode_selection.setCurrentIndex(index)

        return mode_selection

    def _create_indicators_digital_status(self, list_digital_status: list) -> list[QPushButton]:
        """Create the indicators of digital status.

        Parameters
        ----------
        list_digital_status : `list`
            List of the digital status.

        Returns
        -------
        indicators_status : `list` [`PySide6.QtWidgets.QPushButton`]
            Indicators of the digital status.
        """

        indicators_status = list()
        for status in list_digital_status:
            indicator = set_button(status, None, is_indicator=True, is_adjust_size=True)
            self._update_indicator_color(indicator, False)

            indicators_status.append(indicator)

        return indicators_status

    def _update_indicator_color(self, indicator: QPushButton, is_triggered: bool) -> None:
        """Update the color of indicator.

        Parameters
        ----------
        indicator : `PySide6.QtWidgets.QPushButton`
            Indicator.
        is_triggered : `bool`
            The status is triggered or not.
        """

        button_status = ButtonStatus.Normal if is_triggered else ButtonStatus.Default
        update_button_color(indicator, QPalette.Button, button_status)

    def _get_list_digital_status_input(self) -> list:
        """Get the list of digital input status from the bit 0 to 31.

        Returns
        -------
        `list`
            List of the digital input status.
        """

        return [
            "Redundancy OK",
            "Load Distribution OK",
            "Power Supply DC #2 OK",
            "Power Supply DC #1 OK",
            "Power Supply Current #2 OK",
            "Power Supply Current #1 OK",
            "J1-W9-1 Motor Power Breaker OK",
            "J1-W9-2 Motor Power Breaker OK",
            "J1-W9-3 Motor Power Breaker OK",
            "J2-W10-1 Motor Power Breaker OK",
            "J2-W10-2 Motor Power Breaker OK",
            "J2-W10-3 Motor Power Breaker OK",
            "J3-W11-1 Motor Power Breaker OK",
            "J3-W11-2 Motor Power Breaker OK",
            "J3-W11-3 Motor Power Breaker OK",
            "J1-W12-1 Communication Power Breaker OK",
            "Spare Input 16",
            "Spare Input 17",
            "Spare Input 18",
            "Spare Input 19",
            "Spare Input 20",
            "Spare Input 21",
            "Spare Input 22",
            "Spare Input 23",
            "J1-W12-2 Communication Power Breaker OK",
            "J2-W13-1 Communication Power Breaker OK",
            "J2-W13-2 Communication Power Breaker OK",
            "J3-W14-1 Communication Power Breaker OK",
            "J3-W14-2 Communication Power Breaker OK",
            "Spare Input 29",
            "Spare Input 30",
            "Interlock Power Relay On",
        ]

    def _get_list_digital_status_output(self) -> list:
        """Get the list of digital output status from the bit 0 to 7.

        Returns
        -------
        `list`
            List of the digital output status.
        """
        return [
            "Motor Power",
            "Communication Power",
            "Interlock Enable",
            "Reset Motor Breakers",
            "Reset Communication Breakers",
            "Closed-Loop Control",
            "Spare Output 6",
            "Spare Output 7",
        ]

    def _create_controls_digital_status(self, number: int) -> list[QPushButton]:
        """Create the controls of digital status.

        Parameters
        ----------
        number : `int`
            Number of controls.

        Returns
        -------
        controls : `list` [`PySide6.QtWidgets.QPushButton`]
            List of the controls of digital status.
        """

        controls = list()
        for idx in range(number):
            control = set_button("", self._callback_control_digital_status, idx, is_checkable=True)
            self._update_control_text(control, False)

            controls.append(control)

        return controls

    @asyncSlot()
    async def _callback_control_digital_status(self, idx: int) -> None:
        """Callback of the digital-status-control button.

        This allows the user to command individual binary signals to the cell
        regarding breaker resets, individual power supply controls, or
        interlocks.

        Parameters
        ----------
        idx : `int`
            Bit index.
        """

        control = self._digital_status_control[idx]
        is_checked = control.isChecked()

        allowed_mode = LocalMode.Diagnostic
        if self.model.local_mode == allowed_mode:
            is_successful = await run_command(
                self.model.controller.set_bit_digital_status,
                idx,
                DigitalOutputStatus.ToggleBit,
            )
        else:
            await prompt_dialog_warning(
                "_callback_control_digital_status()",
                f"Bit value of digital status can only be set in {allowed_mode!r}.",
            )
            is_successful = False

        if is_successful:
            self._update_control_text(control, is_checked)
        else:
            control.setChecked(not is_checked)

    def _update_control_text(self, control: QPushButton, is_checked: bool) -> None:
        """Update the text of control.

        Parameters
        ----------
        control : `PySide6.QtWidgets.QPushButton`
            Control.
        is_checked : `bool`
            Control is checked or not.
        """

        if is_checked:
            control.setText("ON")
        else:
            control.setText("OFF")

    def create_layout(self) -> QHBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QHBoxLayout`
            Layout.
        """

        layout = QHBoxLayout()

        # First column
        layout_power_force_error = QVBoxLayout()
        layout_power_force_error.addWidget(self._create_group_power_motor())
        layout_power_force_error.addWidget(self._create_group_power_communication())

        layout_power_force_error.addWidget(self._create_group_force_error_load())
        layout_power_force_error.addWidget(self._create_group_force_error_non_load())
        layout_power_force_error.addWidget(self._create_group_force_error_total())

        layout_power_force_error.addWidget(self._button_reboot)

        layout.addLayout(layout_power_force_error)

        # Second column
        layout_digital_status_output = QVBoxLayout()
        layout_digital_status_output.addWidget(self._create_group_digital_status_output())
        layout_digital_status_output.addWidget(self._create_group_digital_status_control())
        layout_digital_status_output.addWidget(self._create_group_control_mode())

        layout.addLayout(layout_digital_status_output)

        # Third column
        layout_digital_status_input_1 = QVBoxLayout()

        num_digital_status_input = len(self._get_list_digital_status_input())
        layout_digital_status_input_1.addWidget(
            self._create_group_digital_status_input(
                0, num_digital_status_input // 2 - 1, "Digital Input Status (I)"
            )
        )

        layout.addLayout(layout_digital_status_input_1)

        # Fourth column
        layout_digital_status_input_2 = QVBoxLayout()
        layout_digital_status_input_2.addWidget(
            self._create_group_digital_status_input(
                num_digital_status_input // 2,
                num_digital_status_input - 1,
                "Digital Input Status (II)",
            )
        )

        layout.addLayout(layout_digital_status_input_2)

        return layout

    def _create_group_power_motor(self) -> QGroupBox:
        """Create the group of motor power.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("Voltage (Calibrated):", self._power_calibrated["power_voltage_motor"])
        layout.addRow("Current (Calibrated):", self._power_calibrated["power_current_motor"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Voltage (Raw):", self._power_raw["power_voltage_motor"])
        layout.addRow("Current (Raw):", self._power_raw["power_current_motor"])

        return create_group_box("Motor Power", layout)

    def _create_group_power_communication(self) -> QGroupBox:
        """Create the group of communication power.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow(
            "Voltage (Calibrated):",
            self._power_calibrated["power_voltage_communication"],
        )
        layout.addRow(
            "Current (Calibrated):",
            self._power_calibrated["power_current_communication"],
        )

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Voltage (Raw):", self._power_raw["power_voltage_communication"])
        layout.addRow("Current (Raw):", self._power_raw["power_current_communication"])

        return create_group_box("Communication Power", layout)

    def _create_group_force_error_load(self) -> QGroupBox:
        """Create the group of force error of individual load link.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("A2:", self._force_error_tangent["a2"])
        layout.addRow("A3:", self._force_error_tangent["a3"])
        layout.addRow("A5:", self._force_error_tangent["a5"])
        layout.addRow("A6:", self._force_error_tangent["a6"])

        return create_group_box("Individual Tangent Weight Error", layout)

    def _create_group_force_error_non_load(self) -> QGroupBox:
        """Create the group of force error of non-load link.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("A1:", self._force_error_tangent["a1"])
        layout.addRow("A4:", self._force_error_tangent["a4"])

        return create_group_box("Non-load Bearing Tangent Error", layout)

    def _create_group_force_error_total(self) -> QGroupBox:
        """Create the group of total force error.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("Total Weight Error:", self._force_error_tangent["total_weight"])
        layout.addRow("Tangent Sum Error:", self._force_error_tangent["tangent_sum"])

        return create_group_box("Summary of Tangent Force Error", layout)

    def _create_group_digital_status_output(self) -> QGroupBox:
        """Create the group of digital output status.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx, indicator in enumerate(self._digital_status_output):
            layout.addRow(f"(D{idx})", indicator)

        return create_group_box("Digital Output Status", layout)

    def _create_group_digital_status_control(self) -> QGroupBox:
        """Create the group of control of digital status.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx, status in enumerate(self._get_list_digital_status_output()):
            layout.addRow(f"(D{idx}) {status}:", self._digital_status_control[idx])

        return create_group_box("Digital Output Controls", layout)

    def _create_group_control_mode(self) -> QGroupBox:
        """Create the group of control of closed-loop control mode.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_control_mode = QFormLayout()
        layout_control_mode.addRow("Mode:", self._control_mode_selection)

        layout = QVBoxLayout()
        layout.addLayout(layout_control_mode)
        layout.addWidget(self._button_update_control_mode)

        return create_group_box("Control Loop", layout)

    def _create_group_digital_status_input(self, idx_start: int, idx_end: int, group_name: str) -> QGroupBox:
        """Create the group of digital input status.

        Parameters
        ----------
        idx_start : `int`
            Start index.
        idx_end : `int`
            End index.
        group_name: `str`
            Group name.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        for idx, indicator in enumerate(self._digital_status_input[idx_start : idx_end + 1]):
            layout.addRow(f"(D{idx + idx_start})", indicator)

        return create_group_box(group_name, layout)

    def _set_signal_utility(self, signal_utility: SignalUtility) -> None:
        """Set the utility signal with callback functions.

        Parameters
        ----------
        signal_utility : `SignalUtility`
            Signal of the utility.
        """

        signal_utility.power_motor_calibrated.connect(self._callback_power_motor_calibrated)
        signal_utility.power_communication_calibrated.connect(self._callback_power_communication_calibrated)

        signal_utility.power_motor_raw.connect(self._callback_power_motor_raw)
        signal_utility.power_communication_raw.connect(self._callback_power_communication_raw)

        signal_utility.digital_status_input.connect(self._callback_digital_status_input)
        signal_utility.digital_status_output.connect(self._callback_digital_status_output)

    @asyncSlot()
    async def _callback_power_motor_calibrated(self, power_motor: tuple) -> None:
        """Callback of the utility signal for the calibrated motor power.

        Parameters
        ----------
        power_motor : `tuple`
            Motor power: (voltage, current). The data type is float. The units
            are volt and ampere respectively.
        """

        self._update_power_motor(self._power_calibrated, power_motor[0], power_motor[1])

    def _update_power_motor(self, power: dict[str, QLabel], voltage: float, current: float) -> None:
        """Update the power of motor.

        Parameters
        ----------
        power : `dict [PySide6.QtWidgets.QLabel]`
            Motor power. The key is the specific power's name.
        voltage : `float`
            Voltage in volt.
        current : `float`
            Current in ampere.
        """

        power["power_voltage_motor"].setText(f"{voltage} V")
        power["power_current_motor"].setText(f"{current} A")

    @asyncSlot()
    async def _callback_power_communication_calibrated(self, power_communication: tuple) -> None:
        """Callback of the utility signal for the communication power.

        Parameters
        ----------
        power_communication : `tuple`
            Communication power: (voltage, current). The data type is float.
            The units are volt and ampere respectively.
        """

        self._update_power_communication(
            self._power_calibrated, power_communication[0], power_communication[1]
        )

    def _update_power_communication(self, power: dict[str, QLabel], voltage: float, current: float) -> None:
        """Update the power of communication.

        Parameters
        ----------
        power : `dict [PySide6.QtWidgets.QLabel]`
            Communication power. The key is the specific power's name.
        voltage : `float`
            Voltage in volt.
        current : `float`
            Current in ampere.
        """

        power["power_voltage_communication"].setText(f"{voltage} V")
        power["power_current_communication"].setText(f"{current} A")

    @asyncSlot()
    async def _callback_power_motor_raw(self, power_motor: tuple) -> None:
        """Callback of the utility signal for the raw motor power.

        Parameters
        ----------
        power_motor : `tuple`
            Motor power: (voltage, current). The data type is float. The units
            are volt and ampere respectively.
        """

        self._update_power_motor(self._power_raw, power_motor[0], power_motor[1])

    @asyncSlot()
    async def _callback_power_communication_raw(self, power_communication: tuple) -> None:
        """Callback of the utility signal for the raw communication power.

        Parameters
        ----------
        power_communication : `tuple`
            Communication power: (voltage, current). The data type is float.
            The units are volt and ampere respectively.
        """

        self._update_power_communication(self._power_raw, power_communication[0], power_communication[1])

    @asyncSlot()
    async def _callback_digital_status_input(self, digital_status_input: int) -> None:
        """Callback of the utility signal for the digital input status.

        Parameters
        ----------
        digital_status_input : `int`
            Digital input status. Each bit means different status. 1 means OK
            or triggered). Otherwise 0.
        """
        self._decode_digital_status(self._digital_status_input, digital_status_input)

    def _decode_digital_status(
        self,
        indicators: list[QPushButton],
        digital_status: int,
        is_digital_status_output: bool = False,
    ) -> None:
        """Decode the digital status and update the related label.

        Parameters
        ----------
        indicators : `list` [`PySide6.QtWidgets.QPushButton`]
            Indicators of the digital status.
        digital_status : `int`
            Digital status. Each bit means different status. 1 means OK or
            triggered). Otherwise 0.
        is_digital_status_output : `bool`, optional
            Is the digital output status or not. (the default is False)
        """

        for bit, indicator in enumerate(indicators):
            is_bit_on = True if digital_status & (2**bit) else False
            self._update_indicator_color(indicator, is_bit_on)

            if is_digital_status_output:
                control = self._digital_status_control[bit]
                control.setChecked(is_bit_on)
                self._update_control_text(control, is_bit_on)

    @asyncSlot()
    async def _callback_digital_status_output(self, digital_status_output: int) -> None:
        """Callback of the utility signal for the digital output status.

        Parameters
        ----------
        digital_status_output : `int`
            Digital output status. Each bit means different status. 1 means OK
            or triggered). Otherwise 0.
        """
        self._decode_digital_status(
            self._digital_status_output,
            digital_status_output,
            is_digital_status_output=True,
        )

    def _set_signal_detailed_force(self, signal_detailed_force: SignalDetailedForce) -> None:
        """Set the detailed force signal with callback function.

        Parameters
        ----------
        signal_detailed_force : `SignalDetailedForce`
            Signal of the detailed force.
        """
        signal_detailed_force.force_error_tangent.connect(self._callback_force_error_tangent)

    @asyncSlot()
    async def _callback_force_error_tangent(self, force_error_tangent: ForceErrorTangent) -> None:
        """Callback of the detailed force signal for tangential force error
        that monitors the supporting force of mirror.

        Parameters
        ----------
        force_error_tangent : `ForceErrorTangent`
            Tangential link force error to monitor the supporting force of
            mirror.
        """

        for idx, force_error_individual in enumerate(force_error_tangent.error_force):
            threshold = (
                TANGENT_LINK_NON_LOAD_BEARING_LINK  # A1, A4
                if idx in (0, 3)
                else TANGENT_LINK_LOAD_BEARING_LINK  # A2, A3, A5, A6
            )

            self._force_error_tangent[f"a{idx + 1}"].setText(
                f"<font color='{self.COLOR_BLACK}'>{force_error_individual} N</font>"
                if abs(force_error_individual) < threshold
                else f"<font color='{self.COLOR_RED}'>{force_error_individual} N</font>"
            )

        self._force_error_tangent["total_weight"].setText(
            f"<font color='{self.COLOR_BLACK}'>{force_error_tangent.error_weight} N</font>"
            if abs(force_error_tangent.error_weight) < TANGENT_LINK_TOTAL_WEIGHT_ERROR
            else f"<font color='{self.COLOR_RED}'>{force_error_tangent.error_weight} N</font>"
        )
        self._force_error_tangent["tangent_sum"].setText(
            f"<font color='{self.COLOR_BLACK}'>{force_error_tangent.error_sum} N</font>"
            if abs(force_error_tangent.error_sum) < TANGENT_LINK_THETA_Z_MOMENT
            else f"<font color='{self.COLOR_RED}'>{force_error_tangent.error_sum} N</font>"
        )

    def _set_signal_closed_loop_control_mode(
        self, signal_closed_loop_control_mode: SignalClosedLoopControlMode
    ) -> None:
        """Set the closed-loop control mode signal.

        Parameters
        ----------
        signal_closed_loop_control_mode : `SignalClosedLoopControlMode`
            Signal to know the closed-loop control mode is updated or not.
        """

        signal_closed_loop_control_mode.is_updated.connect(self._callback_closed_loop_control_mode)

    @asyncSlot()
    async def _callback_closed_loop_control_mode(self, is_updated: bool) -> None:
        """Callback of the closed-loop control mode signal.

        Parameters
        ----------
        is_updated : `bool`
            Closed-loop control mode is updated or not.
        """

        self._control_mode_selection = self._update_index_control_mode_selection(self._control_mode_selection)
