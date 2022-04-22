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

__all__ = ["TabOverview"]

from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import QVBoxLayout, QLabel, QPlainTextEdit
from PySide2.QtGui import QPalette

from ..utils import set_button
from . import TabDefault


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

    def __init__(self, title, model):
        super().__init__(title, model)

        # Message signal
        self._signal_message = None

        # Control signal
        self._signal_control = None

        # Labels
        self._label_control = QLabel()
        self._label_control_mode = QLabel()
        self._label_local_mode = QLabel()

        # Indicators of the system status
        self._indicators_status = self._set_indicators_status()

        # Window to show the log message
        self._window_log = self._set_window_log()

        # Clear the log message on window
        self._button_clear = None

        # Internal layout
        self.widget().setLayout(self._create_layout())

        self._update_control_status()

        self._set_signal_status(self.model.signal_status)

    def _set_indicators_status(self):
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

    def _update_indicator_color(self, indicator, is_status_on):
        """Update the color of indicator.

        Parameters
        ----------
        indicator : `PySide2.QtWidgets.QPushButton`
            Indicator.
        is_status_on : `bool`
            The status is on or off.
        """

        palette = indicator.palette()

        if is_status_on:
            palette.setColor(
                QPalette.Button, self._get_indicator_color_status_on(indicator)
            )
        else:
            palette.setColor(QPalette.Button, Qt.gray)

        indicator.setPalette(palette)

    def _get_indicator_color_status_on(self, indicator):
        """Get the indicator color of the "ON" status.

        This function is to handle the condition that some indicators need the
        different color than others.

        Parameters
        ----------
        indicator : `PySide2.QtWidgets.QPushButton`
            Indicator.

        Returns
        -------
        `PySide2.QtCore.Qt.GlobalColor`
            Color of indicator.
        """

        if indicator.text() == "isAlarmWarningOn":
            return Qt.red
        else:
            return Qt.green

    def _set_window_log(self):
        """Set the log window.

        Returns
        -------
        window_log : `PySide2.QtWidgets.QPlainTextEdit`
            Log message(s) window/widget.
        """

        window_log = QPlainTextEdit()
        window_log.setPlaceholderText("Log Message")
        window_log.setReadOnly(True)

        return window_log

    def _create_layout(self):
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        self._button_clear = set_button("Clear Message", self._callback_clear)

        layout = QVBoxLayout()
        layout.addWidget(self._label_control)
        layout.addWidget(self._label_control_mode)
        layout.addWidget(self._label_local_mode)

        for indicator in self._indicators_status.values():
            layout.addWidget(indicator)

        layout.addWidget(self._window_log)
        layout.addWidget(self._button_clear)

        return layout

    @Slot()
    def _callback_clear(self):
        """Callback of the clear button - removes all log messages from the
        widget."""
        self._window_log.clear()

    def set_signal_message(self, signal_message):
        """Set the message signal.

        Parameters
        ----------
        signal_message : `SignalMessage`
            Signal of the new message.
        """

        self._signal_message = signal_message
        self._signal_message.message.connect(self._callback_signal_message)

    @Slot()
    def _callback_signal_message(self, message):
        """Callback of the message signal.

        Parameters
        ----------
        message : `str`
            Message to log.
        """
        self._window_log.appendPlainText(message)

    def _update_control_status(self):
        """Update the control status."""

        text_control = (
            "Commander is: CSC" if self.model.is_csc_commander else "Commander is: EUI"
        )
        self._label_control.setText(text_control)

        self._label_control_mode.setText(f"Control Mode: {self.model.local_mode.name}")

        text_local_mode = (
            "Control Loop: Closed-Loop Control"
            if self.model.is_closed_loop
            else "Control Loop: Open-Loop Control"
        )
        self._label_local_mode.setText(text_local_mode)

    def _set_signal_status(self, signal_status):
        """Set the status signal.

        Parameters
        ----------
        signal_status : `SignalStatus`
            Signal to know the system status is updated or not.
        """

        signal_status.name_status.connect(self._callback_signal_status)

    @Slot()
    def _callback_signal_status(self, name_status):
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

    def set_signal_control(self, signal_control):
        """Set the control signal.

        Parameters
        ----------
        signal_control : `SignalControl`
            Signal to know the control is updated or not.
        """

        self._signal_control = signal_control
        self._signal_control.is_control_updated.connect(self._callback_signal_control)

    @Slot()
    def _callback_signal_control(self, is_control_updated):
        """Callback of the control signal.

        Parameters
        ----------
        is_control_updated : `bool`
            Control is updated or not.
        """
        self._update_control_status()
