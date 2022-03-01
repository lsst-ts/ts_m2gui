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

__all__ = ["LayoutControl"]

from PySide2 import QtCore
from PySide2.QtWidgets import QVBoxLayout

from ..utils import set_button


class LayoutControl(object):
    """Layout of the control panel.

    Parameters
    ----------
    model : `Model`
        Model class.
    log : `logging.Logger`
        A logger.
    signal_control : `SignalControl`
        Control signal to broadcast the commandable SAL component (CSC) is
        commander or not.

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

        # Send control signal to broadcast the CSC is commander or not
        self._send_signal_control = signal_control

        # Remote button
        self._button_remote = None

        # Local button
        self._button_local = None

        self.layout = self._set_layout()

    def _set_layout(self):
        """Set the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """
        self._button_remote = set_button("Remote", self._callback_remote)
        self._button_local = set_button("Local", self._callback_local)

        layout = QVBoxLayout()
        layout.addWidget(self._button_remote)
        layout.addWidget(self._button_local)

        return layout

    @QtCore.Slot()
    def _callback_remote(self):
        """Callback of the remote button. The commander will be the commandable
        SAL component (CSC)"""
        self.set_csc_commander(True)

    @QtCore.Slot()
    def _callback_local(self):
        """Callback of the local button. The commander will be the graphical
        use interface (GUI)."""
        self.set_csc_commander(False)

    def set_csc_commander(self, is_commander):
        """Set the commandable SAL component (CSC) as the commander.

        If CSC is the commander, graphical user interface (GUI) can not
        control, and vice versa.

        Parameters
        ----------
        is_commander : `bool`
            CSC is the commander or not.
        """

        self.model.is_csc_commander = is_commander

        # Only CSC or GUI can control in a single time
        self._button_remote.setEnabled(not is_commander)
        self._button_local.setEnabled(is_commander)

        # Broadcast the control source
        self._send_signal_control.is_csc_commander.emit(is_commander)

        self.log.info(f"CSC is the commander: {self.model.is_csc_commander}")
