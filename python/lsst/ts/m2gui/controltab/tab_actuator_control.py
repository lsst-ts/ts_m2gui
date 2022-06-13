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

from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QFileDialog,
    QDoubleSpinBox,
    QComboBox,
    QProgressBar,
)

import numpy as np
from pathlib import Path

from ..utils import (
    set_button,
    create_label,
    create_group_box,
    run_command,
    NUM_TANGENT_LINK,
    NUM_ACTUATOR,
)
from ..enums import CommandScript, CommandActuator, ActuatorDisplacementUnit, Ring
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

    MAX_DISPLACEMENT = 10**7

    def __init__(self, title, model):
        super().__init__(title, model)

        self._info_script = {
            "file": create_label(""),
            "progress": self._create_progress_bar(0, 100, 0),
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

        self._target_displacement = self._create_target_displacement()
        self._displacement_unit_selection = self._create_displacement_unit_selection()

        self._ring_selection = self.create_combo_box_ring_selection()
        self._buttons_actuator_selection = self._create_buttons_actuator_selection()
        self._buttons_actuator_selection_support = {
            "select_ring": set_button("Select Ring", self._callback_select_ring),
            "clear_selection": set_button(
                "Clear Selection", self._callback_clear_selection
            ),
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

    def _create_progress_bar(self, value_min, value_max, value_init):
        """Create the progress bar. This will show the execution progress of
        script in the cell controller.

        Parameters
        ----------
        value_min : `float` or `int`
            Minimum value.
        value_max : `float` or `int`
            Maximum value.
        value_init : `float` or `int`
            Initial value.

        Returns
        -------
        progress_bar : `PySide2.QtWidgets.QProgressBar`
            Progress bar.
        """

        progress_bar = QProgressBar()
        progress_bar.setRange(value_min, value_max)
        progress_bar.setValue(value_init)

        return progress_bar

    @Slot()
    def _callback_script_load_script(self, file_name=""):
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

    @Slot()
    def _callback_script_command(self, command):
        """Callback of the command buttons in script control. The cell
        controller will run the related command.

        Parameters
        ----------
        command : enum `CommandScript`
            Script command.
        """

        run_command(self.model.command_script, command)

        if command == CommandScript.Clear:
            self._info_script["file"].setText("")
            self._info_script["progress"].setValue(0)

    def _create_target_displacement(self):
        """Create the target displacement of actuator.

        Returns
        -------
        displacement : `QDoubleSpinBox`
            Target displacement of the actuator.
        """

        displacement = QDoubleSpinBox()
        displacement.setDecimals(
            self.model.utility_monitor.NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT
        )
        displacement.setRange(-self.MAX_DISPLACEMENT, self.MAX_DISPLACEMENT)

        return displacement

    def _create_displacement_unit_selection(self):
        """Create the combo box of displacement unit selection.

        Returns
        -------
        unit_selection : `PySide2.QtWidgets.QComboBox`
            Displacement unit selection.
        """

        unit_selection = QComboBox()

        for displacement_unit in ActuatorDisplacementUnit:
            unit_selection.addItem(displacement_unit.name)

        # Index begins from 0 instead of 1 in QComboBox
        index_mm_unit = ActuatorDisplacementUnit.Millimeter.value - 1
        unit_selection.setCurrentIndex(index_mm_unit)

        unit_selection.currentIndexChanged.connect(self._callback_selection_changed)

        return unit_selection

    @Slot()
    def _callback_selection_changed(self):
        """Callback of the changed selection. This will update the decimals in
        the target displacement."""

        # Index begins from 0 instead of 1 in QComboBox
        selected_unit = ActuatorDisplacementUnit(
            self._displacement_unit_selection.currentIndex() + 1
        )

        if selected_unit == ActuatorDisplacementUnit.Millimeter:
            self._target_displacement.setDecimals(
                self.model.utility_monitor.NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT
            )
        else:
            self._target_displacement.setDecimals(0)

    def _create_buttons_actuator_selection(self):
        """Create the buttons of actuator selection.

        Returns
        -------
        buttons : `list [PySide2.QtWidgets.QPushButton]`
            Buttons of actuators.
        """

        buttons = list()

        actuators = self.model.get_actuator_default_status(False)
        for name in actuators.keys():
            button = set_button(name, None, is_checkable=True, is_adjust_size=True)
            buttons.append(button)

        return buttons

    @Slot()
    def _callback_select_ring(self):
        """Callback of the select-ring button in actuator selector. All
        actuators in the specific ring will be selected."""

        # Index begins from 0 instead of 1 in QComboBox
        ring = Ring(self._ring_selection.currentIndex() + 1)

        for actuator in self._buttons_actuator_selection:
            if actuator.text().startswith(ring.name):
                actuator.setChecked(True)

    @Slot()
    def _callback_clear_selection(self):
        """Callback of the clear-selection button in actuator selector. The
        selected actuators will be cleared/unchecked."""

        for button in self._buttons_actuator_selection:
            button.setChecked(False)

    @Slot()
    def _callback_actuator_start(self):
        """Callback of the start button in actuator control. The cell
        controller will start to move the actuators.

        Returns
        -------
        actuators : `list`
            Selected actuators to do the movement.
        target_displacement : `float` or `int`
            Target displacement of the actuators.
        displacement_unit : enum `ActuatorDisplacementUnit`
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

    @Slot()
    def _callback_actuator_command(self, command):
        """Callback of the actuator buttons in actuator control. The cell
        controller will run the related command.

        Parameters
        ----------
        command : enum `CommandActuator`
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

        layout_control = QGridLayout()
        layout_control.addWidget(self._buttons_script["load_script"], 0, 0)
        layout_control.addWidget(self._buttons_script["stop"], 0, 1)
        layout_control.addWidget(self._buttons_script["resume"], 0, 2)

        layout_control.addWidget(self._buttons_script["run"], 1, 0)
        layout_control.addWidget(self._buttons_script["pause"], 1, 1)
        layout_control.addWidget(self._buttons_script["clear"], 1, 2)

        layout.addLayout(layout_control)

        return create_group_box("Script Control", layout)

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

        # Grid layout of actuator selection
        layout_actuator_selection = QGridLayout()
        layout_actuator_selection.setSpacing(spacing)

        num_row = int(np.ceil(NUM_ACTUATOR / num_column))
        idx = 0
        for row in range(num_row):
            for column in range(num_column):
                if idx < NUM_ACTUATOR:
                    layout_actuator_selection.addWidget(
                        self._buttons_actuator_selection[idx], row, column
                    )
                idx += 1

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

    @Slot()
    def _callback_progress(self, progress):
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

    @Slot()
    def _callback_forces(self, forces):
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
