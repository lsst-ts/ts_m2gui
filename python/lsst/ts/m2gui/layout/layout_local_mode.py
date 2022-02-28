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

__all__ = ["LayoutLocalMode"]

from PySide2 import QtCore
from PySide2.QtWidgets import QVBoxLayout

from ..utils import set_button
from ..enums import LocalMode


class LayoutLocalMode(object):
    """Layout of the local mode.

    Parameters
    ----------
    model : `Model`
        Model class.
    log : `logging.Logger`
        A logger.
    signal_control : `SignalControl`
        Control signal to know the commandable SAL component (CSC) is commander
        or not.

    Attributes
    ----------
    model : `Model`
        Model class.
    log : `logging.Logger`
        A logger.
    layout : `PySide2.QtWidgets.QVBoxLayout`
        Layout.
    """

    def __init__(self, model, log, signal_control):

        self.model = model
        self.log = log

        # Received control signal to know the CSC is commander or not
        self._receive_signal_control = signal_control
        self._receive_signal_control.is_csc_commander.connect(
            self._callback_signal_control
        )

        # Standby button
        self._button_standby = None

        # Diagnostic button
        self._button_diagnostic = None

        # Enable button
        self._button_enable = None

        self.layout = self._set_layout()

    @QtCore.Slot()
    def _callback_signal_control(self, is_csc_commander):
        """Callback of the control signal.

        Parameters
        ----------
        is_csc_commander : `bool`
            Commandable SAL component (CSC) is the commander or not.
        """
        if is_csc_commander:
            self._prohibit_transition()
        else:
            self._update_buttons(self.model.local_mode)

    def _prohibit_transition(self):
        """Prohibit the transition of local mode."""
        self._button_standby.setEnabled(False)
        self._button_diagnostic.setEnabled(False)
        self._button_enable.setEnabled(False)

    def _update_buttons(self, local_mode):
        """Update the buttons.

        Parameters
        ----------
        local_mode : `LocalMode`
            Local mode.

        Raises
        ------
        ValueError
            If the input local mode is not supported.
        """
        if local_mode == LocalMode.Standby:
            self._button_standby.setEnabled(False)
            self._button_diagnostic.setEnabled(True)
            self._button_enable.setEnabled(True)

        elif local_mode == LocalMode.Diagnostic:
            self._button_standby.setEnabled(True)
            self._button_diagnostic.setEnabled(False)
            self._button_enable.setEnabled(True)

        elif local_mode == LocalMode.Enable:
            self._button_standby.setEnabled(True)
            self._button_diagnostic.setEnabled(True)
            self._button_enable.setEnabled(False)

        else:
            raise ValueError(f"Input local mode: {local_mode} is not supported.")

    def _set_layout(self):
        """Set the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        self._button_standby = set_button("Standby", self._callback_standby)
        self._button_diagnostic = set_button("Diagnostic", self._callback_diagnostic)
        self._button_enable = set_button("Enable", self._callback_enable)

        layout = QVBoxLayout()
        layout.addWidget(self._button_standby)
        layout.addWidget(self._button_diagnostic)
        layout.addWidget(self._button_enable)

        return layout

    @QtCore.Slot()
    def _callback_standby(self):
        """Callback of the standby button. The system will transition to the
        standby state."""
        self.set_local_mode(LocalMode.Standby)

    @QtCore.Slot()
    def _callback_diagnostic(self):
        """Callback of the diagnostic button. The system will transition to the
        diagnostic state."""
        self.set_local_mode(LocalMode.Diagnostic)

    @QtCore.Slot()
    def _callback_enable(self):
        """Callback of the enable button. The system will transition to the
        enable state."""
        self.set_local_mode(LocalMode.Enable)

    def set_local_mode(self, local_mode):
        """Set the local mode.

        Parameters
        ----------
        local_mode : `LocalMode`
            Local mode.

        Raises
        ------
        ValueError
            If the input local mode is not supported.
        """

        self.model.local_mode = local_mode
        self._update_buttons(local_mode)

        self.log.info(f"Local mode: {self.model.local_mode!r}")
