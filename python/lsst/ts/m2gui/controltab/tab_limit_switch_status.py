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

__all__ = ["TabLimitSwitchStatus"]

from lsst.ts.guitool import ButtonStatus, create_label, set_button, update_button_color
from lsst.ts.m2com import LimitSwitchType
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout
from qasync import asyncSlot

from ..enums import Ring, Status
from ..model import Model
from ..signals import SignalLimitSwitch
from .tab_default import TabDefault


class TabLimitSwitchStatus(TabDefault):
    """Table of the limit switch status.

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

        # Indicators of the limit switch
        self._indicators_limit_switch_retract = self._create_indicators_limit_switch(
            LimitSwitchType.Retract
        )
        self._indicators_limit_switch_extend = self._create_indicators_limit_switch(
            LimitSwitchType.Extend
        )

        self.set_widget_and_layout(is_scrollable=True)

        # Set the callback of signal
        self._set_signal_limit_switch(self.model.fault_manager.signal_limit_switch)

    def _create_indicators_limit_switch(
        self, limit_switch_type: LimitSwitchType
    ) -> dict[str, QPushButton]:
        """Creates indicators for limit switches.

        Parameters
        ----------
        limit_switch_type : enum `lsst.ts.m2com.LimitSwitchType`
            Type of limit switch.

        Returns
        -------
        indicators : `dict`
            Indicators of limit switch.

        Raises
        ------
        `ValueError`
            Unsupported limit switch type.
        """

        if limit_switch_type == LimitSwitchType.Retract:
            limit_switch_status = self.model.fault_manager.limit_switch_status_retract
        elif limit_switch_type == LimitSwitchType.Extend:
            limit_switch_status = self.model.fault_manager.limit_switch_status_extend
        else:
            raise ValueError(f"Unsupported limit switch type: {limit_switch_type!r}.")

        indicators = dict()
        for name in limit_switch_status.keys():
            indicator = set_button(
                name,
                None,
                is_indicator=True,
                is_adjust_size=True,
                tool_tip="Green: Normal\nYellow: Software limit\nRed: Triggered",
            )

            self._update_indicator_color(indicator, Status.Normal)

            indicators[name] = indicator

        return indicators

    def _update_indicator_color(self, indicator: QPushButton, status: Status) -> None:
        """Update the color of indicator.

        Parameters
        ----------
        indicator : `PySide6.QtWidgets.QPushButton`
            Indicator.
        status : enum `Status`
            Status.
        """

        if status == Status.Normal:
            button_status = ButtonStatus.Normal
        elif status == Status.Alert:
            button_status = ButtonStatus.Warn
        else:
            button_status = ButtonStatus.Error

        update_button_color(indicator, QPalette.Button, button_status)

    def create_layout(self) -> QHBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QHBoxLayout`
            Layout.
        """

        layout = QHBoxLayout()
        for ring in (Ring.B, Ring.C, Ring.D, Ring.A):
            layout.addLayout(
                self._get_layout_limit_switch_specific_ring(
                    LimitSwitchType.Retract, ring
                )
            )
            layout.addLayout(
                self._get_layout_limit_switch_specific_ring(
                    LimitSwitchType.Extend, ring
                )
            )

        return layout

    def _get_layout_limit_switch_specific_ring(
        self, limit_switch_type: LimitSwitchType, ring: Ring
    ) -> QVBoxLayout:
        """Get the layout of limit switch in specific ring.

        Parameters
        ----------
        limit_switch_type : enum `lsst.ts.m2com.LimitSwitchType`
            Type of limit switch.
        ring : enum `Ring`
            Name of ring.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout of limit switch.

        Raises
        ------
        `ValueError`
            Unsupported limit switch type.
        """

        if limit_switch_type == LimitSwitchType.Retract:
            indicators = self._indicators_limit_switch_retract
            label = create_label(name="Retract")
        elif limit_switch_type == LimitSwitchType.Extend:
            indicators = self._indicators_limit_switch_extend
            label = create_label(name="Extend")
        else:
            raise ValueError(f"Unsupported limit switch type: {limit_switch_type!r}.")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(label)
        for name, indicator in indicators.items():
            if name.startswith(ring.name):
                layout.addWidget(indicator)

        return layout

    def _set_signal_limit_switch(self, signal_limit_switch: SignalLimitSwitch) -> None:
        """Set the limit switch signal with callback function.

        Parameters
        ----------
        signal_limit_switch : `SignalLimitSwitch`
            Signal of the limit switch.
        """

        signal_limit_switch.type_name_status.connect(self._callback_signal_limit_switch)

    @asyncSlot()
    async def _callback_signal_limit_switch(self, type_name_status: tuple) -> None:
        """Callback of the limit switch signal.

        Parameters
        ----------
        type_name_status : `tuple`
            A tuple: (type, name, status). The data type of type is integer
            (enum `lsst.ts.m2com.LimitSwitchType`), the data type of name is
            string, and the data type of status is integer (enum `Status`).
        """

        limit_switch_type = LimitSwitchType(type_name_status[0])
        if limit_switch_type == LimitSwitchType.Retract:
            indicators = self._indicators_limit_switch_retract
        elif limit_switch_type == LimitSwitchType.Extend:
            indicators = self._indicators_limit_switch_extend

        name = type_name_status[1]

        self._update_indicator_color(indicators[name], Status(type_name_status[2]))
