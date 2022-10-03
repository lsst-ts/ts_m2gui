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

__all__ = ["TabCellStatus"]

import numpy as np
from lsst.ts.m2com import NUM_ACTUATOR, NUM_TANGENT_LINK, read_yaml_file
from PySide2.QtWidgets import QComboBox, QHBoxLayout, QVBoxLayout
from qasync import asyncSlot

from .. import ActuatorForce
from ..display import FigureConstant, Gauge, ViewMirror
from ..enums import FigureActuatorData
from ..utils import set_button
from . import TabDefault


class TabCellStatus(TabDefault):
    """Table of the cell status.

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

    def __init__(self, title, model):
        super().__init__(title, model)

        self._view_mirror = ViewMirror()
        self._button_show_alias = set_button(
            "Show Alias", self._callback_show_alias, is_checkable=True
        )

        self._forces = ActuatorForce()
        self._figures = self._create_figures()
        self._gauge = Gauge(-1, 1)

        self._actuator_data_selection = self._create_actuator_data_selection()

        # Timer to update cell status forces (and displays)
        self._timer = self.create_and_start_timer(self._callback_time_out)

        # Internal layout
        self.widget().setLayout(self._create_layout())

        # Resize the dock to match the layout size
        self.resize(self.widget().sizeHint())

        self._set_signal_detailed_force(
            self.model.utility_monitor.signal_detailed_force
        )

    @asyncSlot()
    async def _callback_show_alias(self):
        """Callback of the show-alias button. The actuator will show the alias
        or the actuator ID based on this."""

        is_alias = self._button_show_alias.isChecked()
        self._view_mirror.show_alias(is_alias)

    def _create_figures(self, num_realtime=200):
        """Create the figures to show the actuator forces.

        Parameters
        ----------
        num_realtime : `int`, optional
            Number of the realtime data (>=0). (the default is 200)

        Returns
        -------
        figures : `dict`
            Figures of the actuator forces.
        """

        num_axial_actuator = NUM_ACTUATOR - NUM_TANGENT_LINK

        label_x = "Actuator ID"
        label_y = "Force (N)"

        figures = {
            "realtime": FigureConstant(
                1,
                num_realtime,
                num_realtime,
                "Data Point",
                label_y,
                "Absolute Average Force Error",
                legends=["Axial", "Tangent"],
                num_lines=2,
                is_realtime=True,
            ),
            "axial": FigureConstant(
                1,
                num_axial_actuator,
                num_axial_actuator,
                label_x,
                label_y,
                "Axial Actuator",
                legends=[],
            ),
            "tangent": FigureConstant(
                num_axial_actuator + 1,
                num_axial_actuator + NUM_TANGENT_LINK,
                NUM_TANGENT_LINK,
                label_x,
                label_y,
                "Tangent Link",
                legends=[],
            ),
        }

        for figure in figures.values():
            figure.axis_x.setLabelFormat("%d")

        # Only show the axial actuators for every 10 actuators
        figures["axial"].axis_x.setTickCount(np.ceil(num_axial_actuator / 10))

        # Show all the tangent links
        figures["tangent"].axis_x.setTickCount(NUM_TANGENT_LINK)

        return figures

    def _create_actuator_data_selection(self):
        """Create the selection of actuator data.

        Returns
        -------
        actuator_data_selection : `PySide2.QtWidgets.QComboBox`
            Selection of the actuator data.
        """

        actuator_data_selection = QComboBox()
        for specific_data in FigureActuatorData:
            actuator_data_selection.addItem(specific_data.name)

        # Index begins from 0 instead of 1 in QComboBox
        index_force_measured = FigureActuatorData.ForceMeasured.value - 1
        actuator_data_selection.setCurrentIndex(index_force_measured)

        actuator_data_selection.currentIndexChanged.connect(
            self._callback_selection_changed
        )

        return actuator_data_selection

    @asyncSlot()
    async def _callback_selection_changed(self, index):
        """Callback of the changed selection. This will update the actuator
        data on figures.

        Parameters
        ----------
        index : `int`
            Current index.
        """

        data_selected, is_displacement = self._get_data_selected(index=index)
        self._update_figures(data_selected, is_displacement)

        for specific_type in ("axial", "tangent"):
            self._figures[specific_type].adjust_range_axis_y()

    def _get_data_selected(self, index=None):
        """Get the selected actuator data.

        Parameters
        ----------
        index : `int` or None, optional
            Current index. (the default is None)

        Returns
        -------
        `list`
            Selected actuator data. The order is actuator 1 to 78.
        `bool`
            The selected data is the displacement or not. True if yes;
            otherwise, False.
        """

        # Index begins from 0 instead of 1 in QComboBox
        selected_index = (
            self._actuator_data_selection.currentIndex() if index is None else index
        )
        actuator_data = FigureActuatorData(selected_index + 1)

        if actuator_data == FigureActuatorData.ForceMeasured:
            return self._forces.f_cur, False
        elif actuator_data == FigureActuatorData.ForceError:
            return self._forces.f_error, False
        elif actuator_data == FigureActuatorData.Displacement:
            return self._forces.position_in_mm, True

        return list(), False

    def _update_figures(self, values, is_displacement):
        """Update the figures.

        Parameters
        ----------
        values : `list`
            Values to show on figures.
        is_displacement : `bool`
            The selected data is the displacement or not. True if yes;
            otherwise, False.
        """

        # Update the figures of force actuator
        num_axial_actuator = NUM_ACTUATOR - NUM_TANGENT_LINK

        list_x_axial = range(1, num_axial_actuator + 1)
        self._figures["axial"].update_data(list_x_axial, values[:num_axial_actuator])

        list_x_tangent = range(num_axial_actuator + 1, NUM_ACTUATOR + 1)
        self._figures["tangent"].update_data(list_x_tangent, values[-NUM_TANGENT_LINK:])

        for figure_type in ("axial", "tangent"):
            if is_displacement:
                self._figures[figure_type].axis_y.setTitleText("Position (mm)")
            else:
                self._figures[figure_type].axis_y.setTitleText("Force (N)")

    @asyncSlot()
    async def _callback_time_out(self, threshold=50):
        """Callback timeout function to update cell status forces (and
        displays).

        Parameters
        ----------
        threshold : `float` or `int`, optional
            Threshold for minimum/maximum gauge updates. (the default is 50)
        """

        # Cell map
        force_current_min = -1
        force_current_max = 1
        for actuator, force_current in zip(
            self._view_mirror.actuators, self._forces.f_cur
        ):
            actuator.update_magnitude(force_current, self._gauge.min, self._gauge.max)

            # Check the range of current forces
            if force_current < force_current_min:
                force_current_min = force_current

            elif force_current > force_current_max:
                force_current_max = force_current

        # Check we need to update the gauge or not
        if (abs(self._gauge.min - force_current_min) > threshold) or (
            abs(self._gauge.max - force_current_max) > threshold
        ):
            self._gauge.set_magnitude_range(force_current_min, force_current_max)

        # Figures
        num_axial = NUM_ACTUATOR - NUM_TANGENT_LINK
        self._figures["realtime"].append_data(
            np.mean(np.abs(self._forces.f_error[0:num_axial])), idx=0
        )
        self._figures["realtime"].append_data(
            np.mean(np.abs(self._forces.f_error[-NUM_TANGENT_LINK:])), idx=1
        )

        data_selected, is_displacement = self._get_data_selected()
        self._update_figures(data_selected, is_displacement)

        self.check_duration_and_restart_timer(self._timer)

    def _create_layout(self):
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QHBoxLayout()

        # First column
        layout_mirror = QVBoxLayout()
        layout_mirror.addWidget(self._view_mirror)
        layout_mirror.addWidget(self._figures["realtime"])
        layout_mirror.addWidget(self._button_show_alias)

        layout.addLayout(layout_mirror)

        # Second column
        layout.addWidget(self._gauge)

        # Third column
        layout_force = QVBoxLayout()
        layout_force.addWidget(self._figures["axial"])
        layout_force.addWidget(self._figures["tangent"])
        layout_force.addWidget(self._actuator_data_selection)
        layout.addLayout(layout_force)

        return layout

    def read_cell_geometry_file(self, filepath):
        """Read the file of cell geometry.

        Parameters
        ----------
        filepath : `str` or `pathlib.PosixPath`
            Filepath that contains the cell information.

        Raises
        ------
        `IOError`
            Cannot open the file.
        """

        # Read the yaml file
        cell_geometry = read_yaml_file(filepath)

        # Set the mirror radius to calculate the magnification of actuator
        # on the mirror's view
        radius = cell_geometry["radius"]
        self._view_mirror.mirror_radius = radius

        aliases = list(self.model.get_actuator_default_status(False))

        # Axial actuators
        idx_alias = 0
        for id_axial, location in enumerate(cell_geometry["location_axial"]):
            self._view_mirror.add_item_actuator(
                id_axial + 1, aliases[idx_alias], location[0], location[1]
            )
            idx_alias += 1

        # Tangential actuators
        degree_tangent = cell_geometry["degree_tangent"]

        list_id_tangent = range(NUM_ACTUATOR - NUM_TANGENT_LINK + 1, NUM_ACTUATOR + 1)

        angles = np.deg2rad(degree_tangent)
        list_x = radius * np.cos(angles)
        list_y = radius * np.sin(angles)

        for id_tangent, x, y in zip(list_id_tangent, list_x, list_y):
            self._view_mirror.add_item_actuator(id_tangent, aliases[idx_alias], x, y)
            idx_alias += 1

    def _set_signal_detailed_force(self, signal_detailed_force):
        """Set the detailed force signal with callback functions. This signal
        provides the calculated and measured force details contains the look-up
        table (LUT)

        Parameters
        ----------
        signal_detailed_force : `SignalDetailedForce`
            Signal of the detailed force.
        """
        signal_detailed_force.forces.connect(self._callback_forces)

    @asyncSlot()
    async def _callback_forces(self, forces):
        """Callback of the forces, which contain the look-up table (LUT)
        details.

        Parameters
        ----------
        forces : `ActuatorForce`
            Detailed actuator forces.
        """
        self._forces = forces
