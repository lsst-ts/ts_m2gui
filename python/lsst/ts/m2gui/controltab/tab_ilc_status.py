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

__all__ = ["TabIlcStatus"]

import asyncio
from pathlib import Path

import numpy as np
from lsst.ts.m2com import (
    NUM_ACTUATOR,
    NUM_INNER_LOOP_CONTROLLER,
    NUM_TANGENT_LINK,
    read_yaml_file,
)
from lsst.ts.xml.enums import MTM2
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..model import Model
from ..signals import SignalIlcStatus
from ..utils import (
    create_grid_layout_buttons,
    create_group_box,
    create_label,
    run_command,
    set_button,
)
from .tab_default import TabDefault


class TabIlcStatus(TabDefault):
    """Table of the inner-loop controller (ILC) status.

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

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        # Indicators of the ILCs
        self._indicators_ilc = self._create_indicators_ilc(NUM_INNER_LOOP_CONTROLLER)

        # Bypassed ILCs
        self._label_bypassed_ilcs = create_label()

        self._buttons_ilc = {
            "reset": set_button(
                "Reset ILC States",
                self._callback_ilc_state_reset,
                tool_tip=(
                    "Reset the ILC states to NaN. This is recommanded before "
                    "checking the current ILC states."
                ),
            ),
            "check": set_button(
                "Check ILC States",
                self._callback_ilc_state_check,
                tool_tip="Query the controller to get the current ILC states.",
            ),
            "enable": set_button(
                "Enable ILC States",
                self._callback_ilc_state_enable,
                tool_tip="Transition the ILC states to be enabled.",
            ),
        }

        self.set_widget_and_layout()

        # Set the callback of signal
        self._set_signal_ilc_status(self.model.signal_ilc_status)

    def _create_indicators_ilc(self, number: int) -> list[QPushButton]:
        """Creates indicators for the inner-loop controller (ILC).

        Parameters
        ----------
        number : `int`
            Total number of ILC.

        Returns
        -------
        indicators : `list`
            Indicators of ILC.
        """

        indicators = list()

        # ModBUS ID begins from 1 instead of 0
        for specific_id in range(1, number + 1):
            indicator = set_button(
                str(specific_id), None, is_indicator=True, is_adjust_size=True
            )

            self._update_indicator_color(indicator, MTM2.InnerLoopControlMode.Unknown)

            indicators.append(indicator)

        return indicators

    def _update_indicator_color(
        self, indicator: QPushButton, mode: MTM2.InnerLoopControlMode
    ) -> None:
        """Update the color of indicator.

        Parameters
        ----------
        indicator : `PySide2.QtWidgets.QPushButton`
            Indicator.
        mode : enum `MTM2.InnerLoopControlMode`
            Mode of inner-loop controller (ILC).
        """

        palette = indicator.palette()
        palette.setColor(QPalette.Button, self._get_indicator_color(mode))

        indicator.setPalette(palette)

    def _get_indicator_color(self, mode: MTM2.InnerLoopControlMode) -> QColor:
        """Get the indicator color based on the mode.

        Parameters
        ----------
        mode : enum `MTM2.InnerLoopControlMode`
            Mode of inner-loop controller (ILC).

        Returns
        -------
        `PySide2.QtCore.Qt.GlobalColor`
            Indicator color.
        """

        if mode == MTM2.InnerLoopControlMode.Standby:
            return Qt.cyan

        elif mode == MTM2.InnerLoopControlMode.Disabled:
            return Qt.blue

        elif mode == MTM2.InnerLoopControlMode.Enabled:
            return Qt.green

        elif mode == MTM2.InnerLoopControlMode.Fault:
            return Qt.red

        else:
            return Qt.gray

    @asyncSlot()
    async def _callback_ilc_state_reset(self) -> None:
        """Callback of the reset button to reset the inner-loop controller
        (ILC) states to be NaN.
        """

        self._enable_ilc_commands(False)

        self.model.controller.set_ilc_modes_to_nan()
        for indicator in self._indicators_ilc:
            self._update_indicator_color(indicator, MTM2.InnerLoopControlMode.Unknown)

        self._enable_ilc_commands(True)

    def _enable_ilc_commands(self, is_enabled: bool) -> None:
        """Enable the inner-loop controller (ILC) commands or not.

        Parameters
        ----------
        is_enabled : `bool`
            True if enabled. False if disabled.
        """

        for button in self._buttons_ilc.values():
            button.setEnabled(is_enabled)

    @asyncSlot()
    async def _callback_ilc_state_check(self, sleep_time_per_ilc: float = 0.12) -> None:
        """Callback of the check button to check the current inner-loop
        controller (ILC) states in controller.

        Parameters
        ----------
        sleep_time_per_ilc : `float`, optional
            Sleep time per ILC. (the default is 0.12)
        """

        self._enable_ilc_commands(False)

        # Check the ILC states
        addresses = list()
        for idx, mode in enumerate(self.model.controller.ilc_modes):
            if np.isnan(mode) or (mode == MTM2.InnerLoopControlMode.Unknown):
                addresses.append(idx)

        is_checking = False
        num_ilc = len(addresses)
        if num_ilc != 0:
            is_checking = await run_command(
                self.model.controller.get_ilc_modes, addresses
            )

        # Sleep some time when checking the ILC states
        if is_checking:
            await asyncio.sleep(num_ilc * sleep_time_per_ilc)

        self._enable_ilc_commands(True)

    @asyncSlot()
    async def _callback_ilc_state_enable(self) -> None:
        """Callback of the enable button to transition the inner-loop
        controller (ILC) states to be enabled.
        """

        self._enable_ilc_commands(False)

        await run_command(
            self.model.controller.set_ilc_to_enabled,
            reset_nan_first=False,  # type: ignore[arg-type]
            retry_times=self.model.ilc_retry_times,  # type: ignore[arg-type]
            timeout=self.model.ilc_timeout,  # type: ignore[arg-type]
        )

        self._enable_ilc_commands(True)

    def create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()

        # ILC information
        layout.addWidget(self._create_group_ilc_information())

        # Add the groups of grid layout
        num_column = 10
        num_axial_actuators = NUM_ACTUATOR - NUM_TANGENT_LINK
        layout.addWidget(
            self._create_group_grid_layout(
                "Inner-Loop Controller Status (Axial)",
                self._indicators_ilc[0:num_axial_actuators],
                num_column,
            )
        )

        layout.addWidget(
            self._create_group_grid_layout(
                "Inner-Loop Controller Status (Tangent)",
                self._indicators_ilc[num_axial_actuators:NUM_ACTUATOR],
                num_column,
            )
        )

        num_sensors = NUM_INNER_LOOP_CONTROLLER - NUM_ACTUATOR
        layout.addWidget(
            self._create_group_grid_layout(
                "Inner-Loop Controller Status (Sensor)",
                self._indicators_ilc[-num_sensors:],
                num_column,
            )
        )

        # ILC control
        layout.addWidget(self._create_group_ilc_control())

        return layout

    def _create_group_ilc_information(self) -> QGroupBox:
        """Create the group of inner-loop controller (ILC) information.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("ILC Modes:", self._create_label_mode())
        layout.addRow("Bypassed ILCs:", self._label_bypassed_ilcs)

        return create_group_box("Inner-Loop Controller (ILC) Information", layout)

    def _create_label_mode(self) -> QLabel:
        """Create the label of inner-loop controller (ILC) mode.

        Returns
        -------
        label : `PySide2.QtWidgets.QLabel`
            Label of ILC mode.
        """

        # Get the colors for each state
        states = [
            MTM2.InnerLoopControlMode.Standby,
            MTM2.InnerLoopControlMode.Disabled,
            MTM2.InnerLoopControlMode.Enabled,
            MTM2.InnerLoopControlMode.Fault,
            MTM2.InnerLoopControlMode.Unknown,
        ]

        colors = list()
        for state in states:
            colors.append(self._get_indicator_color(state).name.decode())

        # Create the label
        label = create_label("")
        label.setText(
            f"<font color='{colors[0]}'>{states[0].name}</font>, "
            f"<font color='{colors[1]}'>{states[1].name}</font>, "
            f"<font color='{colors[2]}'>{states[2].name}</font>, "
            f"<font color='{colors[3]}'>{states[3].name}</font>, "
            f"<font color='{colors[4]}'>{states[4].name}</font>"
        )

        return label

    def _create_group_grid_layout(
        self, name: str, indicators: list[QPushButton], num_column: int
    ) -> QGroupBox:
        """Create the group of grid layout.

        Parameters
        ----------
        name : `str`
            Name of the group.
        indicators : `list`
            Indicators to put on the grid layout.
        num_column : `int`
            Number of column on the grid layput.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = create_grid_layout_buttons(indicators, num_column)
        return create_group_box(name, layout)

    def _create_group_ilc_control(self) -> QGroupBox:
        """Create the group of inner-loop controller (ILC) control.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QHBoxLayout()
        for button in self._buttons_ilc.values():
            layout.addWidget(button)

        return create_group_box("Inner-Loop Controller Control", layout)

    def _set_signal_ilc_status(self, signal_ilc_status: SignalIlcStatus) -> None:
        """Set the inner-loop controller (ILC) status signal with callback
        function.

        Parameters
        ----------
        signal_ilc_status : `SignalIlcStatus`
            Signal of the ILC status.
        """
        signal_ilc_status.address_mode.connect(
            self._callback_signal_ilc_status_address_mode
        )
        signal_ilc_status.bypassed_ilcs.connect(
            self._callback_signal_ilc_status_bypassed_ilcs
        )

    @asyncSlot()
    async def _callback_signal_ilc_status_address_mode(
        self, address_mode: tuple
    ) -> None:
        """Callback of the inner-loop controller (ILC) status signal for the
        address and mode.

        Parameters
        ----------
        address_mode : `tuple`
            A tuple: (address, mode). The data type of address is integer
            and the data type of mode is integer
            (enum `MTM2.InnerLoopControlMode`).
        """

        address = address_mode[0]
        mode = MTM2.InnerLoopControlMode(address_mode[1])
        self._update_indicator_color(self._indicators_ilc[address], mode)

    @asyncSlot()
    async def _callback_signal_ilc_status_bypassed_ilcs(
        self, bypassed_ilcs: list
    ) -> None:
        """Callback of the inner-loop controller (ILC) status signal for the
        bypassed ILCs.

        Parameters
        ----------
        bypassed_ilcs : `list`
            Bypassed ILCs.
        """

        self._label_bypassed_ilcs.setText(f"{bypassed_ilcs}")

    def read_ilc_details_file(self, filepath: str | Path) -> None:
        """Read the file of inner-loop controller (ILC) details.

        Parameters
        ----------
        filepath : `str` or `pathlib.PosixPath`
            Filepath that contains the ILC information.
        """

        ilc_details = read_yaml_file(filepath)
        for indicator in self._indicators_ilc:
            indicator.setToolTip(ilc_details[f"modBUS_{indicator.text()}"])
