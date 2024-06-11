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

from PySide6.QtWidgets import QVBoxLayout
from qasync import asyncSlot

from ..enums import LocalMode
from ..model import Model
from ..utils import run_command, set_button
from .layout_default import LayoutDefault


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
    layout : `PySide6.QtWidgets.QVBoxLayout`
        Layout.
    """

    def __init__(self, model: Model) -> None:
        # Open-loop button
        self._button_open_loop = set_button(
            "Enter open-loop control",
            self._callback_open_loop,
            tool_tip="No look-up table correction applied",
        )

        # Closed-loop button
        self._button_closed_loop = set_button(
            "Enter closed-loop control",
            self._callback_closed_loop,
            tool_tip="Look-up table correction is applied",
        )

        super().__init__(model)

    @asyncSlot()
    async def _callback_signal_control(self, is_control_updated: bool) -> None:
        if self.model.local_mode in (LocalMode.Standby, LocalMode.Enable):
            self._update_buttons()
        else:
            self._prohibit_control_mode()

    def _update_buttons(self) -> None:
        """Update the buttons."""
        self._button_open_loop.setEnabled(self.model.is_closed_loop)
        self._button_closed_loop.setEnabled(not self.model.is_closed_loop)

    def _prohibit_control_mode(self) -> None:
        """Prohibit the control mode."""
        self._button_open_loop.setEnabled(False)
        self._button_closed_loop.setEnabled(False)

    def _set_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self._button_open_loop)
        layout.addWidget(self._button_closed_loop)

        return layout

    @asyncSlot()
    async def _callback_open_loop(self) -> None:
        """Callback of the open-loop button. The system will turn off the force
        balance system."""
        await self.switch_force_balance_system(False)

    @asyncSlot()
    async def _callback_closed_loop(self) -> None:
        """Callback of the closed-loop button. The system will turn off the
        force balance system."""
        await run_command(self.model.controller.enable_open_loop_max_limit, False)
        await self.switch_force_balance_system(True)

    async def switch_force_balance_system(self, status: bool) -> None:
        """Switch the force balance system.

        Parameters
        ----------
        status : `bool`
            True if turn on the force balance system, which means the system is
            going to do the closed-loop control. Otherwise, False.
        """

        self._prohibit_control_mode()
        is_successful = await run_command(
            self.model.controller.switch_force_balance_system, status
        )

        if not is_successful:
            self._update_buttons()
