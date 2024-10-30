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

__all__ = ["LayoutControl"]

from lsst.ts.guitool import run_command, set_button
from PySide6.QtWidgets import QVBoxLayout
from qasync import asyncSlot

from ..enums import LocalMode
from ..model import Model
from .layout_default import LayoutDefault


class LayoutControl(LayoutDefault):
    """Layout of the control panel.

    Parameters
    ----------
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    layout : `PySide6.QtWidgets.QVBoxLayout`
        Layout.
    """

    def __init__(self, model: Model):
        # Remote button
        self._button_remote = set_button(
            "Remote",
            self._callback_remote,
            tool_tip="Remote control mode by commandable SAL component",
        )

        # Local button
        self._button_local = set_button(
            "Local", self._callback_local, tool_tip="Local control mode by engineer"
        )

        super().__init__(model)

    @asyncSlot()
    async def _callback_signal_control(self, is_control_updated: bool) -> None:
        if self.model.local_mode in (LocalMode.Standby, LocalMode.Enable):
            self._update_buttons()
        else:
            self._prohibit_control()

    def _update_buttons(self) -> None:
        """Update the buttons."""
        self._button_remote.setEnabled(not self.model.is_csc_commander)
        self._button_local.setEnabled(self.model.is_csc_commander)

    def _prohibit_control(self) -> None:
        """Prohibit the control."""
        self._button_remote.setEnabled(False)
        self._button_local.setEnabled(False)

    def _set_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self._button_remote)
        layout.addWidget(self._button_local)

        return layout

    @asyncSlot()
    async def _callback_remote(self) -> None:
        """Callback of the remote button. The commander will be the commandable
        SAL component (CSC)"""
        await self.set_csc_commander(True)

    @asyncSlot()
    async def _callback_local(self) -> None:
        """Callback of the local button. The commander will be the graphical
        use interface (GUI)."""
        await self.set_csc_commander(False)

    async def set_csc_commander(self, is_commander: bool) -> None:
        """Set the commandable SAL component (CSC) as the commander.

        If CSC is the commander, graphical user interface (GUI) can not
        control, and vice versa.

        Parameters
        ----------
        is_commander : `bool`
            CSC is the commander or not.
        """
        await run_command(self.model.controller.switch_command_source, is_commander)
