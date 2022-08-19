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

__all__ = ["TabActuatorControl"]

from pathlib import Path

import numpy as np
from lsst.ts.m2com import (
    NUM_TANGENT_LINK,
    ActuatorDisplacementUnit,
    CommandActuator,
    CommandScript,
)
from PySide2.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QProgressBar,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..enums import Ring
from ..utils import create_group_box, create_label, run_command, set_button
from . import TabDefault


class TabActuatorControl(TabDefault):
    """Table of the actuator control.

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

    MAX_DISPLACEMENT_MM = 200
    MAX_DISPLACEMENT_STEP = 10**7

    def __init__(self, title, model):
        super().__init__(title, model)

        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        self._info_script = {
            "file": create_label(""),
            "progress": progress_bar,
        }

        self._labels_force = {
            "axial_min": create_label(""),
            "axial_max": create_label(""),
            "axial_total": create_label(""),
            "tangent_min": create_label(""),
            "tangent_max": create_label(""),
            "tangent_total": create_label(""),
        }

        self._buttons_script = {
            "load_script": set_button("Load Script", self._callback_script_load_script),
            "run": set_button("Run", self._callback_script_command, CommandScript.Run),
            "stop": set_button(
                "Stop", self._callback_script_command, CommandScript.Stop
            ),
            "pause": set_button(
                "Pause", self._callback_script_command, CommandScript.Pause
            ),
            "resume": set_button(
                "Resume", self._callback_script_command, CommandScript.Resume
            ),
            "clear": set_button(
                "Clear", self._callback_script_command, CommandScript.Clear
            ),
        }

        self._target_displacement = QDoubleSpinBox()

        actuator_displacement_unit = ActuatorDisplacementUnit.Millimeter
        self._set_target_displacement(actuator_displacement_unit)

        self._displacement_unit_selection = self._create_displacement_unit_selection(
            actuator_displacement_unit
        )

        self._ring_selection = self.create_combo_box_ring_selection()
        self._buttons_actuator_selection = [
            set_button(name, None, is_checkable=True, is_adjust_size=True)
            for name in self.model.get_actuator_default_status(False)
        ]

        self._buttons_actuator_selection_support = {
            "select_ring": set_button("Select Ring", self._callback_select_ring),
            "clear_all": set_button("Clear All", self._callback_clear_all),
        }

        self._buttons_actuator = {
            "start": set_button("Start", self._callback_actuator_start),
            "stop": set_button(
                "Stop", self._callback_actuator_command, CommandActuator.Stop
            ),
            "pause": set_button(
                "Pause", self._callback_actuator_command, CommandActuator.Pause
            ),
            "resume": set_button(
                "Resume", self._callback_actuator_command, CommandActuator.Resume
            ),
        }

        self._set_widget_and_layout()

        self._set_signal_script(self.model.signal_script)
        self._set_signal_detailed_force(
            self.model.utility_monitor.signal_detailed_force
        )

    @asyncSlot()
    async def _callback_script_load_script(self, file_name=""):
        """Callback of the load-script button in script control. The cell
        controller will load the script.

        Parameters
        ----------
        file_name : `str`, optional
            File name. This is used for the unit test only. (the default is "")

        Returns
        -------
        name : `str`
            Script name.
        """

        if file_name == "":
            file_name = QFileDialog.getOpenFileName(caption="Select script file")[0]

        name = ""
        if file_name != "":
            # Only the file name is important
            file_path = Path(file_name)
            name = file_path.name

            is_successful = run_command(
                self.model.command_script, CommandScript.LoadScript, name
            )

            if is_successful:
                self._info_script["file"].setText(file_name)

        return name

    @asyncSlot()
    async def _callback_script_command(self, command):
        """Callback of the command buttons in script control. The cell
        controller will run the related command.

        Parameters
        ----------
        command : enum `lsst.ts.m2com.CommandScript`
            Script command.
        """

        run_command(self.model.command_script, command)

        if command == CommandScript.Clear:
            self._info_script["file"].setText("")
            self._info_script["progress"].setValue(0)

    def _set_target_displacement(self, displacement_unit):
        """Set the target displacement.

        The available decimal, range, suffix, and single step in box will be
        updated.

        Parameters
        ----------
        displacement_unit : enum `lsst.ts.m2com.ActuatorDisplacementUnit`
            Actuator displacement unit.

        Raises
        ------
        `ValueError`
            Not supported unit.
        """

        if displacement_unit == ActuatorDisplacementUnit.Millimeter:

            decimal = self.model.utility_monitor.NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT
            max_range = self.MAX_DISPLACEMENT_MM
            suffix = " mm"

        elif displacement_unit == ActuatorDisplacementUnit.Step:

            decimal = 0
            max_range = self.MAX_DISPLACEMENT_STEP
            suffix = " step"

        else:
            raise ValueError(f"Not supported unit: {displacement_unit!r}.")

        self._target_displacement.setDecimals(decimal)
        self._target_displacement.setRange(-max_range, max_range)
        self._target_displacement.setSuffix(suffix)
        self._target_displacement.setSingleStep(10**-decimal)

    def _create_displacement_unit_selection(self, displacement_unit):
        """Create the combo box of displacement unit selection.

        Parameters
        ----------
        displacement_unit : enum `lsst.ts.m2com.ActuatorDisplacementUnit`
            Default actuator displacement unit.

        Returns
        -------
        unit_selection : `PySide2.QtWidgets.QComboBox`
            Displacement unit selection.
        """

        unit_selection = QComboBox()

        for unit in ActuatorDisplacementUnit:
            unit_selection.addItem(unit.name)

        # Index begins from 0 instead of 1 in QComboBox
        index_unit = displacement_unit.value - 1
        unit_selection.setCurrentIndex(index_unit)

        unit_selection.currentIndexChanged.connect(self._callback_selection_changed)

        return unit_selection

    @asyncSlot()
    async def _callback_selection_changed(self, index):
        """Callback of the changed selection. This will update the decimals in
        the target displacement.

        Parameters
        ----------
        index : `int`
            Current index.
        """

        # Index begins from 0 instead of 1 in QComboBox
        selected_unit = ActuatorDisplacementUnit(index + 1)
        self._set_target_displacement(selected_unit)

    @asyncSlot()
    async def _callback_select_ring(self):
        """Callback of the select-ring button in actuator selector. All
        actuators in the specific ring will be selected."""

        # Index begins from 0 instead of 1 in QComboBox
        ring = Ring(self._ring_selection.currentIndex() + 1)

        for actuator in self._buttons_actuator_selection:
            if actuator.text().startswith(ring.name):
                actuator.setChecked(True)

    @asyncSlot()
    async def _callback_clear_all(self):
        """Callback of the clear-all button in actuator selector. All of the
        selected actuators will be cleared/unchecked."""

        for button in self._buttons_actuator_selection:
            button.setChecked(False)

    @asyncSlot()
    async def _callback_actuator_start(self):
        """Callback of the start button in actuator control. The cell
        controller will start to move the actuators.

        Returns
        -------
        actuators : `list`
            Selected actuators to do the movement.
        target_displacement : `float` or `int`
            Target displacement of the actuators.
        displacement_unit : enum `lsst.ts.m2com.ActuatorDisplacementUnit`
            Displacement unit.
        """

        actuators = list()
        for idx, actuator_selection in enumerate(self._buttons_actuator_selection):
            if actuator_selection.isChecked():
                actuators.append(idx)

        target_displacement = self._target_displacement.value()

        # Index begins from 0 instead of 1 in QComboBox
        displacement_unit = ActuatorDisplacementUnit(
            self._displacement_unit_selection.currentIndex() + 1
        )

        run_command(
            self.model.command_actuator,
            CommandActuator.Start,
            actuators,
            target_displacement,
            displacement_unit,
        )

        return actuators, target_displacement, displacement_unit

    @asyncSlot()
    async def _callback_actuator_command(self, command):
        """Callback of the actuator buttons in actuator control. The cell
        controller will run the related command.

        Parameters
        ----------
        command : enum `lsst.ts.m2com.CommandActuator`
            Actuator command.
        """
        run_command(self.model.command_actuator, command)

    def _set_widget_and_layout(self):
        """Set the widget and layout."""

        widget = self.widget()
        widget.setLayout(self._create_layout())

        # Resize the dock to have a similar size of layout
        self.resize(widget.sizeHint())

        self.setWidget(self.set_widget_scrollable(widget, is_resizable=True))

    def _create_layout(self):
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QHBoxLayout`
            Layout.
        """

        layout = QHBoxLayout()

        # First column
        layout_script_control_force_summary = QVBoxLayout()
        layout_script_control_force_summary.addWidget(
            self._create_group_script_control()
        )
        layout_script_control_force_summary.addWidget(
            self._create_group_force_summary()
        )

        layout.addLayout(layout_script_control_force_summary)

        # Second column
        layout_actuator_control = QVBoxLayout()
        layout_actuator_control.addWidget(self._create_group_actuator_selector())
        layout_actuator_control.addWidget(self._create_group_actuator_control())

        layout.addLayout(layout_actuator_control)

        return layout

    def _create_group_script_control(self):
        """Create the group of script control. The cell control system reads
        the binary script to perform a seris of actuator motions.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_file = QFormLayout()
        layout_file.addRow("Script File:", self._info_script["file"])
        layout_file.addRow("Progress:", self._info_script["progress"])

        layout.addLayout(layout_file)

        layout.addLayout(self._create_grid_layout_buttons(self._buttons_script, 3))

        return create_group_box("Script Control", layout)

    def _create_grid_layout_buttons(self, buttons, num_column):
        """Create the grid layout of buttons.

        Parameters
        ----------
        buttons : `dict` or `list`
            Buttons to put on the grid layout.
        num_column : `int`
            Number of column on the grid layput.

        Returns
        -------
        layout : `PySide2.QtWidgets.QGridLayout`
            Grid layout of buttons.
        """

        # Use the list in the following
        if isinstance(buttons, dict):
            items = list(buttons.values())
        else:
            items = buttons

        # Add the item to the layout
        layout = QGridLayout()

        column = 0
        row = 0
        for item in items:
            layout.addWidget(item, row, column)

            column += 1
            if column >= num_column:
                column = 0
                row += 1

        return layout

    def _create_group_force_summary(self):
        """Create the group of force summary. This is just for the high-level
        overview of force status.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        layout.addRow("Minimum Axial (N):", self._labels_force["axial_min"])
        layout.addRow("Maximum Axial (N):", self._labels_force["axial_max"])
        layout.addRow("Total Axial (N):", self._labels_force["axial_total"])

        self.add_empty_row_to_form_layout(layout)

        layout.addRow("Minimum Tangent (N):", self._labels_force["tangent_min"])
        layout.addRow("Maximum Tangent (N):", self._labels_force["tangent_max"])
        layout.addRow("Total Tangent (N):", self._labels_force["tangent_total"])

        return create_group_box("Measured Force Summary", layout)

    def _create_group_actuator_selector(self, spacing=1, num_column=10):
        """Create the group of actuator selector to select single or multiple
        actuators to do the movements.

        Parameters
        ----------
        spacing : `int`, optional
            Spacing between the items on grid layout. (the default is 1)
        num_column : `int`, optional
            Number of column in the grid layout of actuator selection. (the
            default is 10)

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_actuator_selection = self._create_grid_layout_buttons(
            self._buttons_actuator_selection, num_column
        )
        layout_actuator_selection.setSpacing(spacing)

        layout.addLayout(layout_actuator_selection)

        layout.addWidget(self._ring_selection)

        for button in self._buttons_actuator_selection_support.values():
            layout.addWidget(button)

        return create_group_box("Actuator Selector", layout)

    def _create_group_actuator_control(self):
        """Create the group of actuator control for single or multiple
        actuators. This is different from the script control, which focus on a
        continuous motion. This actuator control is just a one-time movement.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_displacement = QFormLayout()
        layout_displacement.addRow("Displacement", self._target_displacement)
        layout_displacement.addRow("Units Select", self._displacement_unit_selection)

        layout.addLayout(layout_displacement)

        for button in self._buttons_actuator.values():
            layout.addWidget(button)

        return create_group_box("Actuator Control", layout)

    def _set_signal_script(self, signal_script):
        """Set the script signal with callback function.

        Parameters
        ----------
        signal_script : `SignalScript`
            Signal of the script progress.
        """
        signal_script.progress.connect(self._callback_progress)

    @asyncSlot()
    async def _callback_progress(self, progress):
        """Callback of the script signal for the progress of script execution.

        Parameters
        ----------
        progress : `int`
            Progress of the script execution (0-100%).
        """
        self._info_script["progress"].setValue(progress)

    def _set_signal_detailed_force(self, signal_detailed_force):
        """Set the detailed force signal with callback function. This signal
        provides the calculated and measured force details contains the look-up
        table (LUT).

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

        force_measured = np.array(forces.f_cur)
        force_axial = force_measured[:-NUM_TANGENT_LINK]
        force_tangent = force_measured[-NUM_TANGENT_LINK:]

        self._labels_force["axial_min"].setText(str(force_axial.min()))
        self._labels_force["axial_max"].setText(str(force_axial.max()))
        self._labels_force["axial_total"].setText(str(force_axial.sum()))

        self._labels_force["tangent_min"].setText(str(force_tangent.min()))
        self._labels_force["tangent_max"].setText(str(force_tangent.max()))
        self._labels_force["tangent_total"].setText(str(force_tangent.sum()))
