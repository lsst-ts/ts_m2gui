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

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QVBoxLayout

from . import LayoutDefault
from ..utils import set_button
from ..enums import LocalMode


class LayoutLocalMode(LayoutDefault):
    """Layout of the local mode.

    Parameters
    ----------
    model : `Model`
        Model class.
    signal_control : `SignalControl`
        Signal to know the control is updated or not.

    Attributes
    ----------
    model : `Model`
        Model class.
    layout : `PySide2.QtWidgets.QVBoxLayout`
        Layout.
    """

    def __init__(self, model, signal_control):

        # Standby button
        self._button_standby = None

        # Diagnostic button
        self._button_diagnostic = None

        # Enable button
        self._button_enable = None

        super().__init__(model, signal_control)

    @Slot()
    def _callback_signal_control(self, is_control_updated):
        if (not self.model.is_csc_commander) and (not self.model.is_closed_loop):
            self._update_buttons()
        else:
            self._prohibit_transition()

    def _update_buttons(self):
        """Update the buttons.

        Raises
        ------
        ValueError
            If the input local mode is not supported.
        """
        local_mode = self.model.local_mode

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

    def _prohibit_transition(self):
        """Prohibit the transition of local mode."""
        self._button_standby.setEnabled(False)
        self._button_diagnostic.setEnabled(False)
        self._button_enable.setEnabled(False)

    def _set_layout(self):
        self._button_standby = set_button(
            "Standby", self._callback_standby, tool_tip="Transition to standby state"
        )
        self._button_diagnostic = set_button(
            "Diagnostic",
            self._callback_diagnostic,
            tool_tip="Transition to diagnostic state",
        )
        self._button_enable = set_button(
            "Enable", self._callback_enable, tool_tip="Transition to enable state"
        )

        layout = QVBoxLayout()
        layout.addWidget(self._button_standby)
        layout.addWidget(self._button_diagnostic)
        layout.addWidget(self._button_enable)

        return layout

    @Slot()
    def _callback_standby(self):
        """Callback of the standby button. The system will transition to the
        standby state."""
        self.model.disable_open_loop_max_limit()
        self.set_local_mode(LocalMode.Standby)

    @Slot()
    def _callback_diagnostic(self):
        """Callback of the diagnostic button. The system will transition to the
        diagnostic state."""
        self.model.disable_open_loop_max_limit()
        self.set_local_mode(LocalMode.Diagnostic)

    @Slot()
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
        self._signal_control.is_control_updated.emit(True)
