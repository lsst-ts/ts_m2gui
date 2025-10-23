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

__all__ = ["TabRigidBodyPos"]

from lsst.ts.guitool import (
    create_double_spin_box,
    create_group_box,
    create_label,
    run_command,
    set_button,
)
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..model import Model
from ..signals import SignalPosition
from .tab_default import TabDefault


class TabRigidBodyPos(TabDefault):
    """Table of the rigid body position.

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

    # Axes of the position
    AXES = ["x", "y", "z", "rx", "ry", "rz"]

    # The following two maximum values (4 mm and 20000 urad) come from the
    # ts_mtm2 that originated by vendor. Need to figure out the details in a
    # latter time.

    # Maximum movement in x, y, or z direction in micrometer (4 mm = 4000 um)
    MAX_DISTANCE_IN_UM = 4000

    # Maximum rotation in rx, ry, or rz direction in arcsec
    # (20000 urad ~ 4125.296 arcsec)
    MAX_ROTATION_IN_ARCSEC = 4125

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        # Relative target position
        self._target_position_relative = self._set_target_position()

        # Absolute target position
        self._target_position_absolute = self._set_target_position()

        # Buttons in this table
        self._buttons = {
            "save_position": set_button("Save Position", self._callback_save_position),
            "go_to_home": set_button("Go to Home", self._callback_go_to_home),
            "set_home": set_button("Set Home", self._callback_set_home),
            "jog": set_button("Jog", self._callback_jog),
            "clear_values_relative": set_button(
                "Clear Values",
                self._callback_clear_values,
                self._target_position_relative,
            ),
            "go_to_position": set_button("Go to Position", self._callback_go_to_position),
            "clear_values_absolute": set_button(
                "Clear Values",
                self._callback_clear_values,
                self._target_position_absolute,
            ),
        }

        # Rigid body position based on the hardpoint displacement
        self._position = self._set_position()

        # Rigid body position based on the independent measurement system (IMS)
        self._position_ims = self._set_position()

        self.set_widget_and_layout()

        self._set_signal_position(self.model.utility_monitor.signal_position)

    def _set_target_position(self) -> dict[str, QDoubleSpinBox]:
        """Set the target position of rigid body.

        Returns
        -------
        position : `dict`
            Target position of the rigid body. The key is the axis. The value
            is the `PySide6.QtWidgets.QDoubleSpinBox`.
        """

        num_digit_after_decimal = self.model.utility_monitor.NUM_DIGIT_AFTER_DECIMAL

        position = dict()
        for axis in self.AXES:
            limit = self.MAX_ROTATION_IN_ARCSEC if axis.startswith("r") else self.MAX_DISTANCE_IN_UM
            position[axis] = create_double_spin_box(
                "", num_digit_after_decimal, maximum=limit, minimum=-limit
            )

        return position

    @asyncSlot()
    async def _callback_save_position(self) -> None:
        """Callback of the save-position button. This will save the current
        position to a file."""
        await run_command(self.model.controller.save_position)

    @asyncSlot()
    async def _callback_go_to_home(self) -> None:
        """Callback of the go-to-home button. This will move the M2 to the
        home position."""
        await run_command(self.model.go_to_position, 0, 0, 0, 0, 0, 0)

    @asyncSlot()
    async def _callback_set_home(self) -> None:
        """Callback of the set-home button. This will set the new home position
        of M2."""
        await run_command(self.model.controller.set_home)

    @asyncSlot()
    async def _callback_jog(self) -> None:
        """Callback of the jog button. This will move the M2 to the new
        position based on the relative offsets."""

        current_position = self.model.utility_monitor.position
        await run_command(
            self.model.go_to_position,
            self._target_position_relative["x"].value() + current_position[0],
            self._target_position_relative["y"].value() + current_position[1],
            self._target_position_relative["z"].value() + current_position[2],
            self._target_position_relative["rx"].value() + current_position[3],
            self._target_position_relative["ry"].value() + current_position[4],
            self._target_position_relative["rz"].value() + current_position[5],
        )

    @asyncSlot()
    async def _callback_clear_values(self, target_positions: dict[str, QDoubleSpinBox]) -> None:
        """Callback of the clear-values button. This will clear the values of
        new target positions.

        Parameters
        ----------
        target_positions : `dict`
            Target positions of the rigid body. The key is the axis. The value
            is the `PySide6.QtWidgets.QDoubleSpinBox`.
        """

        for target_position in target_positions.values():
            target_position.setValue(0)

    @asyncSlot()
    async def _callback_go_to_position(self) -> None:
        """Callback of the go-to-position button. This will move the M2 to the
        new absolute position."""
        await run_command(
            self.model.go_to_position,
            self._target_position_absolute["x"].value(),
            self._target_position_absolute["y"].value(),
            self._target_position_absolute["z"].value(),
            self._target_position_absolute["rx"].value(),
            self._target_position_absolute["ry"].value(),
            self._target_position_absolute["rz"].value(),
        )

    def _set_position(self) -> dict[str, QLabel]:
        """Set the position of rigid body.

        Returns
        -------
        position : `dict`
            Position of the rigid position. The key is the axis. The value is
            the `PySide6.QtWidgets.QLabel`.
        """

        position = dict()
        for axis in self.AXES:
            position[axis] = create_label()

        return position

    def create_layout(self) -> QHBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QHBoxLayout`
            Layout.
        """

        layout = QHBoxLayout()

        # First column
        layout_current_position = QVBoxLayout()
        layout_current_position.addWidget(self._create_group_ims_position())
        layout_current_position.addWidget(self._create_group_current_position())
        layout_current_position.addWidget(self._create_group_home_position())

        layout.addLayout(layout_current_position)

        # Second column
        layout_move_relative = QVBoxLayout()
        layout_move_relative.addWidget(self._create_group_move_relative())

        layout.addLayout(layout_move_relative)

        # Third column
        layout_move_absolute = QVBoxLayout()
        layout_move_absolute.addWidget(self._create_group_move_absolute())

        layout.addLayout(layout_move_absolute)

        return layout

    def _create_group_ims_position(self) -> QGroupBox:
        """Create the group of position based on the independent measurement
        system (IMS).

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_position = QFormLayout()
        for axis in self.AXES:
            if axis.startswith("r"):
                layout_position.addRow(f"Rotation {axis} (arcsec):", self._position_ims[axis])
            else:
                layout_position.addRow(f"Position {axis} (um):", self._position_ims[axis])

        layout = QVBoxLayout()
        layout.addLayout(layout_position)

        return create_group_box("Position Based on Independent Measurement System", layout)

    def _create_group_current_position(self) -> QGroupBox:
        """Create the group of current position.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_position = QFormLayout()
        for axis in self.AXES:
            if axis.startswith("r"):
                layout_position.addRow(f"Rotation {axis} (arcsec):", self._position[axis])
            else:
                layout_position.addRow(f"Position {axis} (um):", self._position[axis])

        layout = QVBoxLayout()
        layout.addLayout(layout_position)
        layout.addWidget(self._buttons["save_position"])

        return create_group_box("Current Position Relative to Home", layout)

    def _create_group_home_position(self) -> QGroupBox:
        """Create the group of home position.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()
        layout.addWidget(self._buttons["go_to_home"])
        layout.addWidget(self._buttons["set_home"])

        return create_group_box("Home Position", layout)

    def _create_group_move_relative(self) -> QGroupBox:
        """Create the group of relative movement to the current position.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_position = QFormLayout()
        for axis in self.AXES:
            if axis.startswith("r"):
                layout_position.addRow(f"Offset {axis} (arcsec):", self._target_position_relative[axis])
            else:
                layout_position.addRow(f"Offset {axis} (um):", self._target_position_relative[axis])

        layout = QVBoxLayout()
        layout.addLayout(layout_position)
        layout.addWidget(self._buttons["jog"])
        layout.addWidget(self._buttons["clear_values_relative"])

        return create_group_box("Move with Offset Relative to Current Position", layout)

    def _create_group_move_absolute(self) -> QGroupBox:
        """Create the group of absolute movement to the home position.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout_position = QFormLayout()
        for axis in self.AXES:
            if axis.startswith("r"):
                layout_position.addRow(f"Rotation {axis} (arcsec):", self._target_position_absolute[axis])
            else:
                layout_position.addRow(f"Position {axis} (um):", self._target_position_absolute[axis])

        layout = QVBoxLayout()
        layout.addLayout(layout_position)
        layout.addWidget(self._buttons["go_to_position"])
        layout.addWidget(self._buttons["clear_values_absolute"])

        return create_group_box("Move to Position Relative to Home", layout)

    def _set_signal_position(self, signal_position: SignalPosition) -> None:
        """Set the position signal with callback function. This signal provides
        the rigid body position.

        Parameters
        ----------
        signal_position : `SignalPosition`
            Signal of the position.
        """

        signal_position.position.connect(self._callback_position)
        signal_position.position_ims.connect(self._callback_position_ims)

    @asyncSlot()
    async def _callback_position(self, position: list) -> None:
        """Callback of the position signal for the rigid body position based on
        the hardpoint displacement.

        Parameters
        ----------
        position : `list`
            Rigid body position as a list: [x, y, z, rx, ry, rz]. The unit of x
            , y, and z is um. The unit of rx, ry, and ry is arcsec.
        """

        for idx, axis in enumerate(self.AXES):
            self._position[axis].setText(str(position[idx]))

    @asyncSlot()
    async def _callback_position_ims(self, position: list) -> None:
        """Callback of the position signal for the rigid body position based on
        the independent measurement system (IMS).

        Parameters
        ----------
        position : `list`
            Rigid body position as a list: [x, y, z, rx, ry, rz]. The unit of x
            , y, and z is um. The unit of rx, ry, and ry is arcsec.
        """

        for idx, axis in enumerate(self.AXES):
            self._position_ims[axis].setText(str(position[idx]))
