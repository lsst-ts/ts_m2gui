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

__all__ = ["LayoutLocalMode"]

from PySide2.QtWidgets import QVBoxLayout
from qasync import asyncSlot

from ..enums import LocalMode
from ..model import Model
from ..utils import run_command, set_button
from .layout_default import LayoutDefault


class LayoutLocalMode(LayoutDefault):
    """Layout of the local mode.

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

    def __init__(self, model: Model) -> None:
        # Standby button
        self._button_standby = set_button(
            "Standby", self._callback_standby, tool_tip="Transition to standby state"
        )

        # Diagnostic button
        self._button_diagnostic = set_button(
            "Diagnostic",
            self._callback_diagnostic,
            tool_tip="Transition to diagnostic state",
        )

        # Enable button
        self._button_enable = set_button(
            "Enable", self._callback_enable, tool_tip="Transition to enable state"
        )

        # The mode transition is in the process or not
        self._is_mode_transition_in_process = False

        super().__init__(model)

    @asyncSlot()
    async def _callback_signal_control(self, is_control_updated: bool) -> None:
        if (
            (not self.model.is_csc_commander)
            and (not self.model.is_closed_loop)
            and (not self._is_mode_transition_in_process)
        ):
            self._update_buttons()
        else:
            self._prohibit_transition()

    def _update_buttons(self) -> None:
        """Update the buttons.

        Raises
        ------
        `ValueError`
            If the input local mode is not supported.
        """
        local_mode = self.model.local_mode

        if local_mode == LocalMode.Standby:
            self._button_standby.setEnabled(False)
            self._button_diagnostic.setEnabled(True)
            self._button_enable.setEnabled(False)

        elif local_mode == LocalMode.Diagnostic:
            self._button_standby.setEnabled(True)
            self._button_diagnostic.setEnabled(False)
            self._button_enable.setEnabled(True)

        elif local_mode == LocalMode.Enable:
            self._button_standby.setEnabled(False)
            self._button_diagnostic.setEnabled(True)
            self._button_enable.setEnabled(False)

        else:
            raise ValueError(f"Input local mode: {local_mode} is not supported.")

    def _prohibit_transition(self) -> None:
        """Prohibit the transition of local mode."""

        self._button_standby.setEnabled(False)
        self._button_diagnostic.setEnabled(False)
        self._button_enable.setEnabled(False)

    def _set_layout(self) -> QVBoxLayout:
        layout = QVBoxLayout()
        layout.addWidget(self._button_standby)
        layout.addWidget(self._button_diagnostic)
        layout.addWidget(self._button_enable)

        return layout

    @asyncSlot()
    async def _callback_standby(self) -> None:
        """Callback of the standby button. The system will transition to the
        standby state."""
        await self.set_local_mode(LocalMode.Standby)

    @asyncSlot()
    async def _callback_diagnostic(self) -> None:
        """Callback of the diagnostic button. The system will transition to the
        diagnostic state."""
        await self.set_local_mode(LocalMode.Diagnostic)

    @asyncSlot()
    async def _callback_enable(self) -> None:
        """Callback of the enable button. The system will transition to the
        enable state."""
        await self.set_local_mode(LocalMode.Enable)

    async def set_local_mode(self, local_mode: LocalMode) -> None:
        """Set the local mode.

        Parameters
        ----------
        local_mode : enum `LocalMode`
            Local mode.

        Raises
        ------
        `ValueError`
            If the input local mode is not supported.
        """

        # Disable all buttons first
        self._is_mode_transition_in_process = True
        self._prohibit_transition()

        # Do the state transition
        if local_mode == LocalMode.Standby:
            command = "exit_diagnostic"

        elif local_mode == LocalMode.Diagnostic:
            command = (
                "enter_diagnostic"
                if self.model.local_mode == LocalMode.Standby
                else "exit_enable"
            )

        elif local_mode == LocalMode.Enable:
            command = "enter_enable"

        await run_command(getattr(self.model, command))

        # Reshow the buttons
        self._is_mode_transition_in_process = False
        self.model.report_control_status()
