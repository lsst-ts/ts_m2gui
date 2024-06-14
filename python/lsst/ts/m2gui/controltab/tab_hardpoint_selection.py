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

__all__ = ["TabHardpointSelection"]

from pathlib import Path

from lsst.ts.m2com import (
    NUM_ACTUATOR,
    NUM_HARDPOINTS_AXIAL,
    NUM_TANGENT_LINK,
    check_hardpoints,
    read_yaml_file,
    select_axial_hardpoints,
)
from PySide6.QtWidgets import QGroupBox, QVBoxLayout
from qasync import asyncSlot

from ..enums import LocalMode
from ..model import Model
from ..signals import SignalDetailedForce
from ..utils import (
    create_grid_layout_buttons,
    create_group_box,
    get_checked_buttons,
    run_command,
    set_button,
)
from .tab_default import TabDefault


class TabHardpointSelection(TabDefault):
    """Table of the hardpoint selection.

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

        self._cell_geom: dict = dict()
        self._hardpoints: list = list()

        self._buttons_hardpoint_selection = [
            set_button(name, None, is_checkable=True, is_adjust_size=True)
            for name in self.model.get_actuator_default_status(False)
        ]
        self._buttons_hardpoint = {
            "reset": set_button(
                "Reset Default",
                self._callback_reset_default,
                tool_tip="Reset the default hardpoints",
            ),
            "apply": set_button(
                "Apply Selection",
                self._callback_apply_hardpoints,
                tool_tip="Apply the selected hardpoints",
            ),
            "suggest": set_button(
                "Suggest Hardpoints",
                self._callback_suggest_hardpoints,
                tool_tip="Suggest the hardpoints",
            ),
        }

        self.set_widget_and_layout()

        self._set_signal_detailed_force(
            self.model.utility_monitor.signal_detailed_force
        )

    @asyncSlot()
    async def _callback_reset_default(self) -> None:
        """Callback of the reset-default button to reset the selection of
        hardpoints back to the default."""

        await run_command(self._set_hardpoints, self._hardpoints)

    def _set_hardpoints(self, hardpoints: list[int]) -> None:
        """Set the hardpoints.

        Parameters
        ----------
        hardpoints : `list`
            List of the 0-based hardpoints. There are 6 actuators. The first
            three are the axial actuators and the latter three are the tangent
            links.
        """

        for idx, hardpoint in enumerate(self._buttons_hardpoint_selection):
            hardpoint.setChecked(idx in hardpoints)

    @asyncSlot()
    async def _callback_apply_hardpoints(self) -> None:
        """Callback of the apply-hardpoints button to apply the selected
        hardpoints."""

        await run_command(self._set_hardpoint_list)

    async def _set_hardpoint_list(self) -> None:
        """Set the hardpoint list.

        Raises
        ------
        `ValueError`
            When do not select 6 hardpoints.
        `RuntimeError`
            When not in the Standby state.
        `RuntimeError`
            When not in the simulation mode.
        """

        # Check the selection
        hardpoints = get_checked_buttons(self._buttons_hardpoint_selection)
        if len(hardpoints) != 6:
            raise ValueError("Please select 6 hardpoints.")

        check_hardpoints(
            self._cell_geom["locAct_axial"],
            hardpoints[:NUM_HARDPOINTS_AXIAL],
            hardpoints[NUM_HARDPOINTS_AXIAL:],
        )

        # Check the state
        allowed_mode = LocalMode.Standby
        if self.model.local_mode != allowed_mode:
            raise RuntimeError(f"Only allowed in {allowed_mode!r}")

        # Set the hardpoints
        await self.model.controller.set_hardpoint_list(hardpoints)

    @asyncSlot()
    async def _callback_suggest_hardpoints(self) -> None:
        """Callback of the suggest-hardpoints button to suggest the possible
        hardpoints."""

        await run_command(self._suggest_hardpoints)

    def _suggest_hardpoints(self) -> None:
        """Suggest the hardpoints. Requires at least one axial and one
        tangential hardpoints are already selected.

        Raises
        ------
        `ValueError`
            When there aren't at least one axial and one tangential actuators
            already selected.
        """

        # Check the axial hardpoint
        num_axial = NUM_ACTUATOR - NUM_TANGENT_LINK
        selection = get_checked_buttons(self._buttons_hardpoint_selection)

        if (len(selection) == 0) or (selection[0] >= num_axial):
            raise ValueError("Please select at least 1 axial hardpoint.")

        suggest_axial = select_axial_hardpoints(
            self._cell_geom["locAct_axial"], selection[0]
        )

        # Check the tangent hardpoint
        hardpoint_tangent = list()
        for idx in selection:
            if idx >= num_axial:
                hardpoint_tangent.append(idx)

        if len(hardpoint_tangent) == 0:
            raise ValueError("Please select at least 1 tagnent hardpoint.")

        option_one = [72, 74, 76]
        option_two = [73, 75, 77]
        suggest_tangent = (
            option_one if (hardpoint_tangent[0] in option_one) else option_two
        )

        # Set the hardpoints
        self._set_hardpoints(suggest_axial + suggest_tangent)

    def create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()

        layout.addWidget(self._create_group_hardpoint_selector())
        layout.addWidget(self._buttons_hardpoint["suggest"])
        layout.addWidget(self._buttons_hardpoint["apply"])
        layout.addWidget(self._buttons_hardpoint["reset"])

        return layout

    def _create_group_hardpoint_selector(
        self, spacing: int = 1, num_column: int = 10
    ) -> QGroupBox:
        """Create the group of hardpoint selector to select the hardpoints.

        Parameters
        ----------
        spacing : `int`, optional
            Spacing between the items on grid layout. (the default is 1)
        num_column : `int`, optional
            Number of column in the grid layout of actuator selection. (the
            default is 10)

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_hardpoint_selection = create_grid_layout_buttons(
            self._buttons_hardpoint_selection, num_column
        )
        layout_hardpoint_selection.setSpacing(spacing)

        layout.addLayout(layout_hardpoint_selection)

        return create_group_box("Hardpoint Selector", layout)

    def _set_signal_detailed_force(
        self, signal_detailed_force: SignalDetailedForce
    ) -> None:
        """Set the detailed force signal with callback function. This signal
        provides the current hardpoints.

        Parameters
        ----------
        signal_detailed_force : `SignalDetailedForce`
            Signal of the detailed force.
        """

        signal_detailed_force.hard_points.connect(self._callback_hardpoints)

    @asyncSlot()
    async def _callback_hardpoints(self, hardpoints: list[int]) -> None:
        """Callback of the hardpoints information.

        Parameters
        ----------
        hardpoints : `list`
            List of the hardpoints. There should be 6 elements. The first
            three are the axial actuators and the last three are the tangential
            actuators.
        """

        # Change the received hardpoints to be 0-based
        self._hardpoints = [(hardpoint - 1) for hardpoint in hardpoints]

        self._set_hardpoints(self._hardpoints)

    def read_cell_geometry_file(self, filepath: str | Path) -> None:
        """Read the file of cell geometry.

        Parameters
        ----------
        filepath : `str` or `pathlib.PosixPath`
            Filepath that contains the cell information.
        """

        self._cell_geom = read_yaml_file(filepath)
