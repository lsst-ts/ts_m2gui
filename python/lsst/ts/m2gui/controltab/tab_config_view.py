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

__all__ = ["TabConfigView"]

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QVBoxLayout

from ..utils import create_label
from . import TabDefault


class TabConfigView(TabDefault):
    """Table of the configuration view.

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

        # Labels
        self._label_file_configuration = create_label()
        self._label_file_version = create_label()
        self._label_file_control_parameters = create_label()
        self._label_file_lut_parameters = create_label()

        self._label_power_warning_motor = create_label()
        self._label_power_fault_motor = create_label()
        self._label_power_threshold_motor = create_label()

        self._label_power_warning_communication = create_label()
        self._label_power_fault_communication = create_label()
        self._label_power_threshold_communication = create_label()

        self._label_in_position_axial = create_label()
        self._label_in_position_tangent = create_label()
        self._label_in_position_sample = create_label()

        self._label_timeout_sal = create_label()
        self._label_timeout_crio = create_label()
        self._label_timeout_ilc = create_label()

        self._label_misc_range_angle = create_label()
        self._label_misc_diff_enabled = create_label()

        self._label_misc_range_temperature = create_label()

        # Internal widget and layout
        self._set_widget_and_layout()

        # Set the callback of signal
        self._set_signal_config(self.model.signal_config)

    def _set_widget_and_layout(self):
        """Set the widget and layout."""

        widget = self.widget()
        widget.setLayout(self._create_layout())
        self.setWidget(self.set_widget_scrollable(widget, is_resizable=True))

    def _create_layout(
        self, point_size_section=12, point_size_subsection=11, space_between_sections=30
    ):
        """Create the layout.

        Parameters
        ----------
        point_size_section : `int`, optional
            Point size of the section. (the default is 12)
        point_size_subsection : `int`, optional
            Point size of the subsection. (the default is 11)
        space_between_sections : `int`, optional
            Space between the sections. (the default is 30)

        Returns
        -------
        layout : `PySide2.QtWidgets.QVBoxLayout`
            Layout.
        """

        layout = QVBoxLayout()

        label_file_version = create_label(
            name="File Paths and Version", point_size=point_size_section, is_bold=True
        )
        layout.addWidget(label_file_version)
        layout.addWidget(self._label_file_configuration)
        layout.addWidget(self._label_file_version)
        layout.addWidget(self._label_file_control_parameters)
        layout.addWidget(self._label_file_lut_parameters)

        layout.addSpacing(space_between_sections)

        label_power_supply = create_label(
            name="Power Supply Monitoring", point_size=point_size_section, is_bold=True
        )
        layout.addWidget(label_power_supply)

        label_power_motor = create_label(
            name="Motor", point_size=point_size_subsection, is_bold=True
        )
        layout.addWidget(label_power_motor)
        layout.addWidget(self._label_power_warning_motor)
        layout.addWidget(self._label_power_fault_motor)
        layout.addWidget(self._label_power_threshold_motor)

        label_power_communication = create_label(
            name="Communication", point_size=point_size_subsection, is_bold=True
        )
        layout.addWidget(label_power_communication)
        layout.addWidget(self._label_power_warning_communication)
        layout.addWidget(self._label_power_fault_communication)
        layout.addWidget(self._label_power_threshold_communication)

        layout.addSpacing(space_between_sections)

        label_in_position_flag = create_label(
            name="In-Position Flag", point_size=point_size_section, is_bold=True
        )
        layout.addWidget(label_in_position_flag)
        layout.addWidget(self._label_in_position_axial)
        layout.addWidget(self._label_in_position_tangent)
        layout.addWidget(self._label_in_position_sample)

        layout.addSpacing(space_between_sections)

        label_communication_timeout = create_label(
            name="Communication Timeout", point_size=point_size_section, is_bold=True
        )
        layout.addWidget(label_communication_timeout)
        layout.addWidget(self._label_timeout_sal)
        layout.addWidget(self._label_timeout_crio)
        layout.addWidget(self._label_timeout_ilc)

        layout.addSpacing(space_between_sections)

        label_miscellaneous = create_label(
            name="Miscellaneous", point_size=point_size_section, is_bold=True
        )
        layout.addWidget(label_miscellaneous)

        label_inclinometer = create_label(
            name="Inclinometer", point_size=point_size_subsection, is_bold=True
        )
        layout.addWidget(label_inclinometer)
        layout.addWidget(self._label_misc_range_angle)
        layout.addWidget(self._label_misc_diff_enabled)

        label_temperature = create_label(
            name="Temperature", point_size=point_size_subsection, is_bold=True
        )
        layout.addWidget(label_temperature)
        layout.addWidget(self._label_misc_range_temperature)

        return layout

    def _set_signal_config(self, signal_config):
        """Set the config signal with callback function.

        Parameters
        ----------
        signal_config : `SignalConfig`
            Signal of the configuration.
        """

        signal_config.config.connect(self._callback_signal_config)

    @Slot()
    def _callback_signal_config(self, config):
        """Callback of the config signal for the new configuration.

        Parameters
        ----------
        config : `Config`
            New configuration.
        """

        self._label_file_configuration.setText(
            f"File of Configuration: {config.file_configuration}"
        )
        self._label_file_version.setText(
            f"Configuration Version: {config.file_version}"
        )
        self._label_file_control_parameters.setText(
            f"Control Parameters: {config.file_control_parameters}"
        )
        self._label_file_lut_parameters.setText(
            f"Look-Up Table Parameters: {config.file_lut_parameters}"
        )

        self._label_power_warning_motor.setText(
            f"24V Accuracy Warning: {config.power_warning_motor} %"
        )
        self._label_power_fault_motor.setText(
            f"24V Accuracy Fault: {config.power_fault_motor} %"
        )
        self._label_power_threshold_motor.setText(
            f"Current Threshold: {config.power_threshold_motor} A"
        )

        self._label_power_warning_communication.setText(
            f"24V Accuracy Warning: {config.power_warning_communication} %"
        )
        self._label_power_fault_communication.setText(
            f"24V Accuracy Fault: {config.power_fault_communication} %"
        )
        self._label_power_threshold_communication.setText(
            f"Current Threshold: {config.power_threshold_communication} A"
        )

        self._label_in_position_axial.setText(
            f"Axial Threshold: {config.in_position_axial} N"
        )
        self._label_in_position_tangent.setText(
            f"Tangent Threshold: {config.in_position_tangent} N"
        )
        self._label_in_position_sample.setText(
            f"Sample Window: {config.in_position_sample} s"
        )

        self._label_timeout_sal.setText(
            f"SAL Communication Timeout: {config.timeout_sal} s"
        )
        self._label_timeout_crio.setText(
            f"cRIO Communication Timeout: {config.timeout_crio} s"
        )
        self._label_timeout_ilc.setText(
            f"ILC Telemetry Receipt Error Persistance: {int(config.timeout_ilc)} counts"
        )

        self._label_misc_range_angle.setText(
            f"Delta Range: {config.misc_range_angle} degree"
        )
        self._label_misc_diff_enabled.setText(
            f"Difference Enabled: {config.misc_diff_enabled}"
        )

        self._label_misc_range_temperature.setText(
            f"Cell Temperature Delta: {config.misc_range_temperature} degree C"
        )
