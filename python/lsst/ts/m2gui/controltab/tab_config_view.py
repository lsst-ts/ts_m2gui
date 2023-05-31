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

__all__ = ["TabConfigView"]

from PySide2.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QVBoxLayout,
)
from qasync import asyncSlot

from ..config import Config
from ..enums import LocalMode
from ..model import Model
from ..signals import SignalConfig
from ..utils import (
    create_group_box,
    create_label,
    prompt_dialog_warning,
    run_command,
    set_button,
)
from .tab_default import TabDefault


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

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        # List of the configuration files
        self._list_files = QListWidget()

        # Button to set the configuration file
        self._button_set_file = set_button(
            "Set Configuration File", self._callback_set_configuration_file
        )

        # Configuration parameters
        self._config_parameters = {
            "file_configuration": create_label(),
            "file_version": create_label(),
            "file_control_parameters": create_label(),
            "file_lut_parameters": create_label(),
            "power_warning_motor": create_label(),
            "power_fault_motor": create_label(),
            "power_threshold_motor": create_label(),
            "power_warning_communication": create_label(),
            "power_fault_communication": create_label(),
            "power_threshold_communication": create_label(),
            "in_position_axial": create_label(),
            "in_position_tangent": create_label(),
            "in_position_sample": create_label(),
            "timeout_sal": create_label(),
            "timeout_crio": create_label(),
            "timeout_ilc": create_label(),
            "misc_range_angle": create_label(),
            "misc_diff_enabled": create_label(),
            "misc_range_temperature": create_label(),
        }

        self._set_widget_and_layout()

        self._set_signal_config(self.model.signal_config)

    @asyncSlot()
    async def _callback_set_configuration_file(self) -> None:
        """Callback to set the configuration file."""

        file = self._get_selected_file()
        function_name = "_callback_set_configuration_file()"
        if file == "":
            await prompt_dialog_warning(
                function_name,
                "Please select a configuration file.",
            )
            return

        allowed_mode = LocalMode.Standby
        if self.model.local_mode == allowed_mode:
            await run_command(self.model.controller.set_configuration_file, file)
        else:
            await prompt_dialog_warning(
                function_name,
                f"Configuration file can only be set in {allowed_mode!r}.",
            )

    def _get_selected_file(self) -> str:
        """Get the selected configuration file.

        Returns
        -------
        `str`
            Selected configuration file.
        """

        selected_file = self._list_files.selectedItems()
        return selected_file[0].text() if (len(selected_file) != 0) else ""

    def _set_widget_and_layout(self) -> None:
        """Set the widget and layout."""

        widget = self.widget()
        widget.setLayout(self._create_layout())

        # Resize the dock to have a similar size of layout
        self.resize(widget.sizeHint())

    def _create_layout(self) -> QHBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide2.QtWidgets.QHBoxLayout`
            Layout.
        """

        layout = QHBoxLayout()

        # First column
        layout_file = QVBoxLayout()
        layout_file.addWidget(self._create_group_configuration_files())
        layout_file.addWidget(self._create_group_file_version())

        layout.addLayout(layout_file)

        # Second column
        layout_content = QVBoxLayout()
        layout_content.addWidget(self._create_group_power_motor())
        layout_content.addWidget(self._create_group_power_communication())
        layout_content.addWidget(self._create_group_in_position_flag())
        layout_content.addWidget(self._create_group_communication_timeout())
        layout_content.addWidget(self._create_group_misc_inclinometer())
        layout_content.addWidget(self._create_group_misc_temperature())

        layout.addLayout(layout_content)

        return layout

    def _create_group_configuration_files(self) -> QGroupBox:
        """Create the group of configuration files.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()
        layout.addWidget(self._list_files)
        layout.addWidget(self._button_set_file)

        return create_group_box("Configuration Files", layout)

    def _create_group_file_version(self) -> QGroupBox:
        """Create the group of files and version.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow(
            "Configuration File:", self._config_parameters["file_configuration"]
        )
        layout.addRow("Configuration Version:", self._config_parameters["file_version"])
        layout.addRow(
            "Control Parameters:", self._config_parameters["file_control_parameters"]
        )
        layout.addRow(
            "Look-Up Table Parameters:", self._config_parameters["file_lut_parameters"]
        )

        return create_group_box("File Paths and Version", layout)

    def _create_group_power_motor(self) -> QGroupBox:
        """Create the group of motor power.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow(
            "24V Accuracy Warning:", self._config_parameters["power_warning_motor"]
        )
        layout.addRow(
            "24V Accuracy Fault:", self._config_parameters["power_fault_motor"]
        )
        layout.addRow(
            "Current Threshold:", self._config_parameters["power_threshold_motor"]
        )

        return create_group_box("Motor Power Supply Monitoring", layout)

    def _create_group_power_communication(self) -> QGroupBox:
        """Create the group of communication power.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow(
            "24V Accuracy Warning:",
            self._config_parameters["power_warning_communication"],
        )
        layout.addRow(
            "24V Accuracy Fault:", self._config_parameters["power_fault_communication"]
        )
        layout.addRow(
            "Current Threshold:",
            self._config_parameters["power_threshold_communication"],
        )

        return create_group_box("Communication Power Supply Monitoring", layout)

    def _create_group_in_position_flag(self) -> QGroupBox:
        """Create the group of in-position flag.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Axial Threshold:", self._config_parameters["in_position_axial"])
        layout.addRow(
            "Tangent Threshold:", self._config_parameters["in_position_tangent"]
        )
        layout.addRow("Sample Window:", self._config_parameters["in_position_sample"])

        return create_group_box("In-Position Flag", layout)

    def _create_group_communication_timeout(self) -> QGroupBox:
        """Create the group of communication timeout.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow(
            "SAL Communication Timeout:", self._config_parameters["timeout_sal"]
        )
        layout.addRow(
            "cRIO Communication Timeout:", self._config_parameters["timeout_crio"]
        )
        layout.addRow(
            "ILC Telemetry Receipt Error Persistance:",
            self._config_parameters["timeout_ilc"],
        )

        return create_group_box("Communication Timeout", layout)

    def _create_group_misc_inclinometer(self) -> QGroupBox:
        """Create the group of miscellaneous of inclinometer.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Delta Range:", self._config_parameters["misc_range_angle"])
        layout.addRow(
            "Difference Enabled:", self._config_parameters["misc_diff_enabled"]
        )

        return create_group_box("Miscellaneous (Inclinometer)", layout)

    def _create_group_misc_temperature(self) -> QGroupBox:
        """Create the group of miscellaneous of temperature.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow(
            "Cell Temperature Delta:",
            self._config_parameters["misc_range_temperature"],
        )

        return create_group_box("Miscellaneous (Temperature)", layout)

    def _set_signal_config(self, signal_config: SignalConfig) -> None:
        """Set the config signal with callback function. This signal provides
        the details of configuration in the controller.

        Parameters
        ----------
        signal_config : `SignalConfig`
            Signal of the configuration.
        """

        signal_config.files.connect(self._callback_signal_config_files)
        signal_config.config.connect(self._callback_signal_config)

    @asyncSlot()
    async def _callback_signal_config_files(self, files: list[str]) -> None:
        """Callback of the config signal for the configuration files.

        Parameters
        ----------
        files : `list`
            Configuration files.
        """

        self._list_files.clear()
        for file in files:
            self._list_files.addItem(file)

    @asyncSlot()
    async def _callback_signal_config(self, config: Config) -> None:
        """Callback of the config signal for the new configuration.

        Parameters
        ----------
        config : `Config`
            New configuration.
        """

        self._config_parameters["file_configuration"].setText(
            f"{config.file_configuration}"
        )
        self._config_parameters["file_version"].setText(f"{config.file_version}")
        self._config_parameters["file_control_parameters"].setText(
            f"{config.file_control_parameters}"
        )
        self._config_parameters["file_lut_parameters"].setText(
            f"{config.file_lut_parameters}"
        )

        self._config_parameters["power_warning_motor"].setText(
            f"{config.power_warning_motor} %"
        )
        self._config_parameters["power_fault_motor"].setText(
            f"{config.power_fault_motor} %"
        )
        self._config_parameters["power_threshold_motor"].setText(
            f"{config.power_threshold_motor} A"
        )

        self._config_parameters["power_warning_communication"].setText(
            f"{config.power_warning_communication} %"
        )
        self._config_parameters["power_fault_communication"].setText(
            f"{config.power_fault_communication} %"
        )
        self._config_parameters["power_threshold_communication"].setText(
            f"{config.power_threshold_communication} A"
        )

        self._config_parameters["in_position_axial"].setText(
            f"{config.in_position_axial} N"
        )
        self._config_parameters["in_position_tangent"].setText(
            f"{config.in_position_tangent} N"
        )
        self._config_parameters["in_position_sample"].setText(
            f"{config.in_position_sample} s"
        )

        self._config_parameters["timeout_sal"].setText(f"{config.timeout_sal} s")
        self._config_parameters["timeout_crio"].setText(f"{config.timeout_crio} s")
        self._config_parameters["timeout_ilc"].setText(
            f"{int(config.timeout_ilc)} counts"
        )

        self._config_parameters["misc_range_angle"].setText(
            f"{config.misc_range_angle} degree"
        )
        self._config_parameters["misc_diff_enabled"].setText(
            f"{config.misc_diff_enabled}"
        )

        self._config_parameters["misc_range_temperature"].setText(
            f"{config.misc_range_temperature} degree C"
        )
