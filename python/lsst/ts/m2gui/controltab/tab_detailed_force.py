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

__all__ = ["TabDetailedForce"]

from lsst.ts.guitool import create_group_box, create_label, create_table
from lsst.ts.m2com import NUM_ACTUATOR, NUM_TANGENT_LINK
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..actuator_force_axial import ActuatorForceAxial
from ..actuator_force_tangent import ActuatorForceTangent
from ..enums import Ring
from ..model import Model
from ..signals import SignalDetailedForce
from ..utils import get_num_actuator_ring
from .tab_default import TabDefault


class TabDetailedForce(TabDefault):
    """Table of the detailed force.

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

    # These are constants used in the self._resize_table() before figuring out
    # an easy way to resize the table smartly.
    MIN_WIDTH = 600
    MIN_HEIGHT = 400

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        # List of the hard points
        self._hard_points = {
            "axial": create_label(),
            "tangent": create_label(),
        }

        # Detailed forces of the table widget items
        self._forces = self._create_items_force()

        # Latest received actuator forces
        self._forces_latest_axial = ActuatorForceAxial()
        self._forces_latest_tangent = ActuatorForceTangent()

        # List of the force details
        self._list_force_details = list(self._forces.keys())

        # Select the ring to show the detailed force
        self._ring_selection = self.create_combo_box_ring_selection(self._callback_selection_changed)

        # Table of the detailed force
        self._table_forces = self._create_table_forces()

        # Timer to update the forces on table
        self._timer = self.create_and_start_timer(self._callback_time_out, self.model.duration_refresh)

        self.set_widget_and_layout(is_scrollable=True)

        self._set_signal_detailed_force(self.model.utility_monitor.signal_detailed_force)

    def _create_items_force(self) -> dict[str, list[QTableWidgetItem]]:
        """Create the items of force.

        Returns
        -------
        items_force : `dict`
            Items of the force. The value is the list of
            `PySide6.QtWidgets.QTableWidgetItem`.
        """

        actuator_id = list()
        for ring in (Ring.B, Ring.C, Ring.D, Ring.A):
            num_actuator = get_num_actuator_ring(ring)
            actuator_id += [QTableWidgetItem(ring.name + str(idx)) for idx in range(1, num_actuator + 1)]

        items_force = dict()
        items_force["id"] = actuator_id

        for name in vars(self.model.utility_monitor.forces_axial).keys():
            items_force[name] = list()
            for idx in range(NUM_ACTUATOR):
                items_force[name].append(QTableWidgetItem())

        return items_force

    @asyncSlot()
    async def _callback_selection_changed(self, index: int) -> None:
        """Callback of the changed selection. This will scroll the table to
        make sure the user can see the actuators of selected ring.

        Parameters
        ----------
        index : `int`
            Current index.
        """

        # Index begins from 0 instead of 1 in QComboBox
        ring = Ring(index + 1)
        name_first_actuator = ring.name + "1"

        items = self._table_forces.findItems(name_first_actuator, Qt.MatchExactly)
        if len(items) != 0:
            self._table_forces.scrollToItem(items[0], hint=QAbstractItemView.PositionAtTop)

    def _create_table_forces(self) -> QTableWidget:
        """Create the table widget of detailed forces.

        Returns
        -------
        `PySide6.QtWidgets.QTableWidget`
            Table widget.
        """

        table = create_table(self._list_force_details, is_disabled_selection=True)
        table = self._add_detailed_force_to_table(table)

        return self._resize_table(table)

    def _add_detailed_force_to_table(self, table: QTableWidget) -> QTableWidget:
        """Add the detailed force to table.

        Parameters
        ----------
        table : `PySide6.QtWidgets.QTableWidget`
            Table widget without the items.

        Returns
        -------
        table : `PySide6.QtWidgets.QTableWidget`
            Table widget with the items.
        """

        table.setRowCount(NUM_ACTUATOR)

        num_items = len(self._list_force_details)
        for row in range(NUM_ACTUATOR):
            for column in range(num_items):
                table.setItem(row, column, self._forces[self._list_force_details[column]][row])

        return table

    def _resize_table(self, table: QTableWidget) -> QTableWidget:
        """Resize the table.

        Parameters
        ----------
        table : `PySide6.QtWidgets.QTableWidget`
            Table widget.

        Returns
        -------
        table : `PySide6.QtWidgets.QTableWidget`
            Resized table widget.
        """

        table.setMinimumWidth(self.MIN_WIDTH)
        table.setMinimumHeight(self.MIN_HEIGHT)

        return table

    @asyncSlot()
    async def _callback_time_out(self) -> None:
        """Callback timeout function to update the force table."""

        # Update the force items on tables
        num_axial_actuator = NUM_ACTUATOR - NUM_TANGENT_LINK
        self._update_forces(self._forces_latest_axial, num_axial_actuator)
        self._update_forces(self._forces_latest_tangent, NUM_TANGENT_LINK)

        self.check_duration_and_restart_timer(self._timer, self.model.duration_refresh)

    def _update_forces(
        self,
        forces_latest: ActuatorForceAxial | ActuatorForceTangent,
        num_actuator: int,
    ) -> None:
        """Update the forces.

        Parameters
        ----------
        forces_latest : `ActuatorForceAxial` or `ActuatorForceTangent`
            Latest data of the axial or tangent actuator forces.
        num_actuator : `int`
            Number of the actuators.
        """

        # Check the "forces" is the axial actuator or not
        num_axial_actuator = NUM_ACTUATOR - NUM_TANGENT_LINK
        is_axial_actuator = num_actuator == num_axial_actuator

        for key in vars(forces_latest).keys():
            field = getattr(forces_latest, key)

            for idx in range(num_actuator):
                # Need to add the index's offset for tangent links
                idx_updated = idx if is_axial_actuator else (num_axial_actuator + idx)

                if key in ("encoder_count", "step"):
                    self._forces[key][idx_updated].setText(str(field[idx]))
                elif key == "position_in_mm":
                    self._forces[key][idx_updated].setText("%.4f" % field[idx])
                else:
                    self._forces[key][idx_updated].setText("%.2f" % field[idx])

    def create_layout(self) -> QVBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()

        layout_hard_points = QVBoxLayout()
        layout_hard_points.addWidget(self._create_hard_points())

        layout.addLayout(layout_hard_points)

        layout.addWidget(self._ring_selection)
        layout.addWidget(self._table_forces)

        return layout

    def _create_hard_points(self) -> QGroupBox:
        """Create the group of hard points.

        Returns
        -------
        group : `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Axial:", self._hard_points["axial"])
        layout.addRow("Tangent:", self._hard_points["tangent"])

        return create_group_box("Hard Points", layout)

    def _set_signal_detailed_force(self, signal_detailed_force: SignalDetailedForce) -> None:
        """Set the detailed force signal with callback functions. This signal
        provides the calculated and measured force details contains the look-up
        table (LUT)

        Parameters
        ----------
        signal_detailed_force : `SignalDetailedForce`
            Signal of the detailed force.
        """

        signal_detailed_force.hard_points.connect(self._callback_hard_points)

        signal_detailed_force.forces_axial.connect(self._callback_forces_axial)
        signal_detailed_force.forces_tangent.connect(self._callback_forces_tangent)

    @asyncSlot()
    async def _callback_hard_points(self, hard_points: list[int]) -> None:
        """Callback of the hard points (axial and tangential directions).

        Parameters
        ----------
        hard_points : `list`
            List of the hard points. There should be 6 elements. The first
            three are the axial actuators and the last three are the tangential
            actuators.
        """

        self._hard_points["axial"].setText(f"{hard_points[:3]}")
        self._hard_points["tangent"].setText(f"{hard_points[3:]}")

    @asyncSlot()
    async def _callback_forces_axial(self, forces: ActuatorForceAxial) -> None:
        """Callback of the axial forces, which contain the look-up table (LUT)
        details.

        Parameters
        ----------
        forces : `ActuatorForceAxial`
            Detailed axial actuator forces.
        """
        self._forces_latest_axial = forces

    @asyncSlot()
    async def _callback_forces_tangent(self, forces: ActuatorForceTangent) -> None:
        """Callback of the tangent forces, which contain the look-up table
        (LUT) details.

        Parameters
        ----------
        forces : `ActuatorForceTangent`
            Detailed tangent actuator forces.
        """
        self._forces_latest_tangent = forces
