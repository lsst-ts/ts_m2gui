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

__all__ = ["TabOverview"]

from lsst.ts.guitool import ButtonStatus, create_label, set_button, update_button_color
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QPlainTextEdit, QPushButton, QVBoxLayout
from qasync import asyncSlot

from ..model import Model
from ..signals import (
    SignalClosedLoopControlMode,
    SignalControl,
    SignalMessage,
    SignalStatus,
)
from .tab_default import TabDefault


class TabOverview(TabDefault):
    """Table of the overview.

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

        # Labels
        self._label_control = create_label()
        self._label_control_mode = create_label()
        self._label_local_mode = create_label(
            name=f"Control Loop: {self.model.controller.closed_loop_control_mode.name}"
        )
        self._label_inclination_source = create_label()

        # Indicators of the system status
        self._indicators_status = self._set_indicators_status()

        # Window to show the log message
        self._window_log = self._set_window_log()

        # Clear the log message on window
        self._button_clear = None

        self.set_widget_and_layout()

        self._update_control_status()

        self._set_signal_status(self.model.signal_status)
        self._set_signal_closed_loop_control_mode(
            self.model.signal_closed_loop_control_mode
        )

    def _set_indicators_status(self) -> dict[str, QPushButton]:
        """Set the indicators of system status.

        Returns
        -------
        indicators_status : `dict`
            Indicators of the system status.
        """

        indicators_status = dict()
        for name in self.model.system_status.keys():
            indicators_status[name] = set_button(
                name, None, is_indicator=True, is_adjust_size=True
            )

        # Adjust the width of indicators and fill the default color
        width_max = 0
        for indicator in indicators_status.values():
            width_indicator = indicator.width()
            if width_max < indicator.width():
                width_max = width_indicator

            self._update_indicator_color(indicator, False)

        for indicator in indicators_status.values():
            indicator.setMaximumWidth(width_max)

        return indicators_status

    def _update_indicator_color(
        self, indicator: QPushButton, is_status_on: bool
    ) -> None:
        """Update the color of indicator.

        Parameters
        ----------
        indicator : `PySide6.QtWidgets.QPushButton`
            Indicator.
        is_status_on : `bool`
            The status is on or off.
        """

        button_statue = (
            self._get_indicator_status_on(indicator)
            if is_status_on
            else ButtonStatus.Default
        )
        update_button_color(indicator, QPalette.Button, button_statue)

    def _get_indicator_status_on(self, indicator: QPushButton) -> ButtonStatus:
        """Get the indicator status of the "ON" status.

        This function is to handle the condition that some indicators need the
        different color than others.

        Parameters
        ----------
        indicator : `PySide6.QtWidgets.QPushButton`
            Indicator.

        Returns
        -------
        `lsst.ts.guitool.ButtonStatus`
            Button status.
        """

        if indicator.text() in (
            "isAlarmOn",
            "isCellTemperatureHigh",
            "isInterlockEngaged",
        ):
            return ButtonStatus.Error

        elif indicator.text() == "isWarningOn":
            return ButtonStatus.Warn

        else:
            return ButtonStatus.Normal

    def _set_window_log(self) -> QPlainTextEdit:
        """Set the log window.

        Returns
        -------
        window_log : `PySide6.QtWidgets.QPlainTextEdit`
            Log message(s) window/widget.
        """

        window_log = QPlainTextEdit()
        window_log.setPlaceholderText("Log Message")
        window_log.setReadOnly(True)

        return window_log

    def create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout.
        """

        self._button_clear = set_button("Clear Message", self._callback_clear)

        layout = QVBoxLayout()
        layout.addWidget(self._label_control)
        layout.addWidget(self._label_control_mode)
        layout.addWidget(self._label_local_mode)
        layout.addWidget(self._label_inclination_source)

        for indicator in self._indicators_status.values():
            layout.addWidget(indicator)

        layout.addWidget(self._window_log)
        layout.addWidget(self._button_clear)

        return layout

    @asyncSlot()
    async def _callback_clear(self) -> None:
        """Callback of the clear button - removes all log messages from the
        widget."""
        self._window_log.clear()

    def set_signal_message(self, signal_message: SignalMessage) -> None:
        """Set the message signal.

        Parameters
        ----------
        signal_message : `SignalMessage`
            Signal of the new message.
        """

        signal_message.message.connect(self._callback_signal_message)

    @asyncSlot()
    async def _callback_signal_message(self, message: str) -> None:
        """Callback of the message signal.

        Parameters
        ----------
        message : `str`
            Message to log.
        """
        self._window_log.appendPlainText(message)

    def _update_control_status(self) -> None:
        """Update the control status."""

        text_control = (
            "Commander is: CSC" if self.model.is_csc_commander else "Commander is: EUI"
        )
        self._label_control.setText(text_control)

        self._label_control_mode.setText(f"Control Mode: {self.model.local_mode.name}")

        self._label_inclination_source.setText(
            f"Inclination Source: {self.model.inclination_source.name}"
        )

    def _set_signal_status(self, signal_status: SignalStatus) -> None:
        """Set the status signal.

        Parameters
        ----------
        signal_status : `SignalStatus`
            Signal to know the system status is updated or not.
        """

        signal_status.name_status.connect(self._callback_signal_status)

    @asyncSlot()
    async def _callback_signal_status(self, name_status: tuple) -> None:
        """Callback of the status signal.

        Parameters
        ----------
        name_status : `tuple`
            A tuple: (name, status). The data type of name is string and the
            data type of status is bool.
        """

        self._update_indicator_color(
            self._indicators_status[name_status[0]], name_status[1]
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

        signal_closed_loop_control_mode.is_updated.connect(
            self._callback_closed_loop_control_mode
        )

    @asyncSlot()
    async def _callback_closed_loop_control_mode(self, is_updated: bool) -> None:
        """Callback of the closed-loop control mode signal.

        Parameters
        ----------
        is_updated : `bool`
            Closed-loop control mode is updated or not.
        """

        self._label_local_mode.setText(
            f"Control Loop: {self.model.controller.closed_loop_control_mode.name}"
        )

    def set_signal_control(self, signal_control: SignalControl) -> None:
        """Set the control signal.

        Parameters
        ----------
        signal_control : `SignalControl`
            Signal to know the control is updated or not.
        """

        signal_control.is_control_updated.connect(self._callback_signal_control)

    @asyncSlot()
    async def _callback_signal_control(self, is_control_updated: bool) -> None:
        """Callback of the control signal.

        Parameters
        ----------
        is_control_updated : `bool`
            Control is updated or not.
        """
        self._update_control_status()
