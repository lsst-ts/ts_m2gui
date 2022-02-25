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

__all__ = ["LayoutControlMode"]

from PySide2 import QtCore
from PySide2.QtWidgets import QVBoxLayout

from ..utils import set_button


class LayoutControlMode(object):
    """Layout of the control mode.

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

        # Open-loop button
        self._button_open_loop = None

        # Closed-loop button
        self._button_closed_loop = None

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
            self._prohibit_control_mode()
        else:
            self._update_buttons(self.model.force_balance_system_status)

    def _prohibit_control_mode(self):
        """Prohibit the control mode."""
        self._button_open_loop.setEnabled(False)
        self._button_closed_loop.setEnabled(False)

    def _update_buttons(self, status):
        """Update the buttons.

        Parameters
        ----------
        status : `bool`
            True if the force balance system is on. Otherwise, False.

        Raises
        ------
        ValueError
            If the input local mode is not supported.
        """
        self._button_open_loop.setEnabled(status)
        self._button_closed_loop.setEnabled(not status)

    def _set_layout(self):
        """Set the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        self._button_open_loop = set_button(
            "Enter open-loop control", self._callback_open_loop
        )
        self._button_closed_loop = set_button(
            "Enter closed-loop control", self._callback_closed_loop
        )

        layout = QVBoxLayout()
        layout.addWidget(self._button_open_loop)
        layout.addWidget(self._button_closed_loop)

        return layout

    @QtCore.Slot()
    def _callback_open_loop(self):
        """Callback of the open-loop button. The system will turn off the force
        balance system."""
        self.switch_force_balance_system(False)

    @QtCore.Slot()
    def _callback_closed_loop(self):
        """Callback of the closed-loop button. The system will turn off the
        force balance system."""
        self.switch_force_balance_system(True)

    def switch_force_balance_system(self, status):
        """Switch the force balance system.

        Parameters
        ----------
        status : `bool`
            True if turn on the force balance system. Otherwise, False.

        Returns
        -------
        result : `bool`
            True if succeeds. Otherwise, False.
        """

        self.model.force_balance_system_status = status
        self._update_buttons(status)

        self.log.info(
            f"Force balance system status: {self.model.force_balance_system_status}"
        )
