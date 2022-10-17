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

__all__ = ["LayoutControlMode"]

from PySide2.QtWidgets import QVBoxLayout
from qasync import asyncSlot

from ..enums import LocalMode
from ..utils import run_command, set_button
from . import LayoutDefault


class LayoutControlMode(LayoutDefault):
    """Layout of the control mode.

    Parameters
    ----------
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    layout : `PySide2.QtWidgets.QVBoxLayout`
        Layout.
    """

    def __init__(self, model):

        # Open-loop button
        self._button_open_loop = None

        # Closed-loop button
        self._button_closed_loop = None

        super().__init__(model)

    @asyncSlot()
    async def _callback_signal_control(self, is_control_updated):
        if self.model.local_mode == LocalMode.Enable:
            self._update_buttons()
        else:
            self._prohibit_control_mode()

    def _update_buttons(self):
        """Update the buttons."""
        self._button_open_loop.setEnabled(self.model.is_closed_loop)
        self._button_closed_loop.setEnabled(not self.model.is_closed_loop)

    def _prohibit_control_mode(self):
        """Prohibit the control mode."""
        self._button_open_loop.setEnabled(False)
        self._button_closed_loop.setEnabled(False)

    def _set_layout(self):
        self._button_open_loop = set_button(
            "Enter open-loop control",
            self._callback_open_loop,
            tool_tip="No look-up table correction applied",
        )
        self._button_closed_loop = set_button(
            "Enter closed-loop control",
            self._callback_closed_loop,
            tool_tip="Look-up table correction is applied",
        )

        layout = QVBoxLayout()
        layout.addWidget(self._button_open_loop)
        layout.addWidget(self._button_closed_loop)

        return layout

    @asyncSlot()
    async def _callback_open_loop(self):
        """Callback of the open-loop button. The system will turn off the force
        balance system."""
        await self.switch_force_balance_system(False)

    @asyncSlot()
    async def _callback_closed_loop(self):
        """Callback of the closed-loop button. The system will turn off the
        force balance system."""
        await self.switch_force_balance_system(True)

    async def switch_force_balance_system(self, status):
        """Switch the force balance system.

        Parameters
        ----------
        status : `bool`
            True if turn on the force balance system, which means the system is
            going to do the closed-loop control. Otherwise, False.
        """
        await run_command(
            self.model.controller.write_command_to_server,
            "switchForceBalanceSystem",
            message_details={"status": status},
        )
