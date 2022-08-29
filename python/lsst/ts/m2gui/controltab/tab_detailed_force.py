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

from lsst.ts.m2com import NUM_ACTUATOR
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QTableWidgetItem,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..enums import Ring
from ..utils import create_group_box, create_label, create_table, get_num_actuator_ring
from . import TabDefault


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

    def __init__(self, title, model):
        super().__init__(title, model)

        # List of the hard points
        self._hard_points = {
            "axial": create_label(),
            "tangent": create_label(),
        }

        # Detailed force
        self._forces = self._create_items_force()

        # List of the force details
        self._list_force_details = list(self._forces.keys())

        # Select the ring to show the detailed force
        self._ring_selection = self.create_combo_box_ring_selection(
            self._callback_selection_changed
        )

        # Table of the detailed force
        self._table_forces = self._create_table_forces()

        self._set_widget_and_layout()

        self._set_signal_detailed_force(
            self.model.utility_monitor.signal_detailed_force
        )

    def _create_items_force(self):
        """Create the items of force.

        Returns
        -------
        items_force : `dict`
            Items of the force. The value is the `list` of
            `PySide2.QtWidgets.QTableWidgetItem`.
        """

        actuator_id = list()
        for ring in (Ring.B, Ring.C, Ring.D, Ring.A):
            num_actuator = get_num_actuator_ring(ring)
            actuator_id += [
                QTableWidgetItem(ring.name + str(idx))
                for idx in range(1, num_actuator + 1)
            ]

        items_force = dict()
        items_force["id"] = actuator_id

        for name in vars(self.model.utility_monitor.forces).keys():
            items_force[name] = list()
            for idx in range(NUM_ACTUATOR):
                items_force[name].append(QTableWidgetItem())

        return items_force

    @asyncSlot()
    async def _callback_selection_changed(self, index):
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
            self._table_forces.scrollToItem(
                items[0], hint=QAbstractItemView.PositionAtTop
            )

    def _create_table_forces(self):
        """Create the table widget of detailed forces.

        Returns
        -------
        `PySide2.QtWidgets.QTableWidget`
            Table widget.
        """

        table = create_table(self._list_force_details, is_disabled_selection=True)
        table = self._add_detailed_force_to_table(table)

        return self._resize_table(table)

    def _add_detailed_force_to_table(self, table):
        """Add the detailed force to table.

        Parameters
        ----------
        table : `PySide2.QtWidgets.QTableWidget`
            Table widget without the items.

        Returns
        -------
        table : `PySide2.QtWidgets.QTableWidget`
            Table widget with the items.
        """

        table.setRowCount(NUM_ACTUATOR)

        num_items = len(self._list_force_details)
        for row in range(NUM_ACTUATOR):
            for column in range(num_items):
                table.setItem(
                    row, column, self._forces[self._list_force_details[column]][row]
                )

        return table

    def _resize_table(self, table):
        """Resize the table.

        Parameters
        ----------
        table : `PySide2.QtWidgets.QTableWidget`
            Table widget.

        Returns
        -------
        table : `PySide2.QtWidgets.QTableWidget`
            Resized table widget.
        """

        table.setMinimumWidth(self.MIN_WIDTH)
        table.setMinimumHeight(self.MIN_HEIGHT)

        return table

    def _set_widget_and_layout(self):
        """Set the widget and layout."""

        widget = self.widget()
        widget.setLayout(self._create_layout())

        self.setWidget(self.set_widget_scrollable(widget, is_resizable=True))

    def _create_layout(self):
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QHBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()

        layout_hard_points = QVBoxLayout()
        layout_hard_points.addWidget(self._create_hard_points())

        layout.addLayout(layout_hard_points)

        layout.addWidget(self._ring_selection)
        layout.addWidget(self._table_forces)

        return layout

    def _create_hard_points(self):
        """Create the group of hard points.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Axial:", self._hard_points["axial"])
        layout.addRow("Tangent:", self._hard_points["tangent"])

        return create_group_box("Hard Points", layout)

    def _set_signal_detailed_force(self, signal_detailed_force):
        """Set the detailed force signal with callback functions. This signal
        provides the calculated and measured force details contains the look-up
        table (LUT)

        Parameters
        ----------
        signal_detailed_force : `SignalDetailedForce`
            Signal of the detailed force.
        """

        signal_detailed_force.hard_points.connect(self._callback_hard_points)
        signal_detailed_force.forces.connect(self._callback_forces)

    @asyncSlot()
    async def _callback_hard_points(self, hard_points):
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
    async def _callback_forces(self, forces):
        """Callback of the forces, which contain the look-up table (LUT)
        details.

        Parameters
        ----------
        forces : `ActuatorForce`
            Detailed actuator forces.
        """

        for key in vars(forces).keys():
            field = getattr(forces, key)

            is_interger = key in ("encoder_count", "step")

            for idx in range(NUM_ACTUATOR):
                if is_interger:
                    self._forces[key][idx].setText(str(field[idx]))
                else:
                    self._forces[key][idx].setText("%.2f" % field[idx])
