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

from pathlib import Path

from lsst.ts.m2com import (
    NUM_ACTUATOR,
    NUM_INNER_LOOP_CONTROLLER,
    NUM_TANGENT_LINK,
    InnerLoopControlMode,
    read_yaml_file,
)
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QGroupBox, QLabel, QPushButton, QVBoxLayout
from qasync import asyncSlot

from ..model import Model
from ..signals import SignalIlcStatus
from ..utils import (
    create_grid_layout_buttons,
    create_group_box,
    create_label,
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

        # Internal layout
        self.widget().setLayout(self._create_layout())

        # Resize the dock to have a similar size of layout
        self.resize(self.widget().sizeHint())

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

            self._update_indicator_color(indicator, InnerLoopControlMode.Unknown)

            indicators.append(indicator)

        return indicators

    def _update_indicator_color(
        self, indicator: QPushButton, mode: InnerLoopControlMode
    ) -> None:
        """Update the color of indicator.

        Parameters
        ----------
        indicator : `PySide2.QtWidgets.QPushButton`
            Indicator.
        mode : enum `lsst.ts.m2com.InnerLoopControlMode`
            Mode of inner-loop controller (ILC).
        """

        palette = indicator.palette()
        palette.setColor(QPalette.Button, self._get_indicator_color(mode))

        indicator.setPalette(palette)

    def _get_indicator_color(self, mode: InnerLoopControlMode) -> QColor:
        """Get the indicator color based on the mode.

        Parameters
        ----------
        mode : enum `lsst.ts.m2com.InnerLoopControlMode`
            Mode of inner-loop controller (ILC).

        Returns
        -------
        `PySide2.QtCore.Qt.GlobalColor`
            Indicator color.
        """

        if mode == InnerLoopControlMode.Standby:
            return Qt.cyan

        elif mode == InnerLoopControlMode.Disabled:
            return Qt.blue

        elif mode == InnerLoopControlMode.Enabled:
            return Qt.green

        elif mode == InnerLoopControlMode.Fault:
            return Qt.red

        else:
            return Qt.gray

    def _create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()
        layout.addWidget(self._create_label_mode())

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

        return layout

    def _create_label_mode(self) -> QLabel:
        """Create the label of inner-loop controller (ILC) mode.

        Returns
        -------
        label : `PySide2.QtWidgets.QLabel`
            Label of ILC mode.
        """

        # Get the colors for each state
        states = [
            InnerLoopControlMode.Standby,
            InnerLoopControlMode.Disabled,
            InnerLoopControlMode.Enabled,
            InnerLoopControlMode.Fault,
            InnerLoopControlMode.Unknown,
        ]

        colors = list()
        for state in states:
            colors.append(self._get_indicator_color(state).name.decode())

        # Create the label
        label = create_label("")
        label.setText(
            "Inner-Loop Controller Mode: "
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

    def _set_signal_ilc_status(self, signal_ilc_status: SignalIlcStatus) -> None:
        """Set the inner-loop controller (ILC) status signal with callback
        function.

        Parameters
        ----------
        signal_ilc_status : `SignalIlcStatus`
            Signal of the ILC status.
        """
        signal_ilc_status.address_mode.connect(self._callback_signal_ilc_status)

    @asyncSlot()
    async def _callback_signal_ilc_status(self, address_mode: tuple) -> None:
        """Callback of the inner-loop controller (ILC) status signal.

        Parameters
        ----------
        address_mode : `tuple`
            A tuple: (address, mode). The data type of address is integer
            and the data type of mode is integer
            (enum `lsst.ts.m2com.InnerLoopControlMode`).
        """

        address = address_mode[0]
        mode = InnerLoopControlMode(address_mode[1])
        self._update_indicator_color(self._indicators_ilc[address], mode)

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
