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

__all__ = ["TabSettings"]

from lsst.ts.guitool import (
    LOG_LEVEL_MAXIMUM,
    LOG_LEVEL_MINIMUM,
    POINT_SIZE_MAXIMUM,
    POINT_SIZE_MINIMUM,
    PORT_MAXIMUM,
    PORT_MINIMUM,
    REFRESH_FREQUENCY_MAXIMUM,
    REFRESH_FREQUENCY_MINIMUM,
    TIMEOUT_MINIMUM,
    create_double_spin_box,
    create_group_box,
    run_command,
    set_button,
)
from lsst.ts.m2com import (
    NUM_TEMPERATURE_EXHAUST,
    NUM_TEMPERATURE_INTAKE,
    NUM_TEMPERATURE_RING,
)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
)
from qasync import QApplication, asyncSlot

from ..model import Model
from ..signals import SignalConfig
from .tab_default import TabDefault


class TabSettings(TabDefault):
    """Table of the settings.

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

    # The unit is degree
    ANGLE_DIFFERENCE_MINIMUM = 1
    ANGLE_DIFFERENCE_MAXIMUM = 10

    # The unit is degree C
    TEMPERATURE_REFERENCE_MINIMUM = -30.0
    TEMPERATURE_REFERENCE_MAXIMUM = 30.0

    # The unit is degree
    EXTERNAL_ELEVATION_ANGLE_MINIMUM = 0.0
    EXTERNAL_ELEVATION_ANGLE_MAXIMUM = 90.0

    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        self._settings = self._create_settings()

        self._button_apply_host = set_button("Apply Host Settings", self._callback_apply_host)
        self._button_apply_control_parameters = set_button(
            "Apply Control Parameters",
            self._callback_apply_control_parameters,
            tool_tip=(
                "This will function when setting the control parameters to\n"
                "the low-level controller (Standby state -> Diagnostic state)."
            ),
        )
        self._button_apply_temperature_reference = set_button(
            "Apply Temperature Reference",
            self._callback_apply_temperature_reference,
            tool_tip=("Apply the temperature reference value used in the look-up\ntable (LUT) calculation."),
        )

        self._button_overwrite_external_elevation_angle = set_button(
            "Overwrite External Elevation Angle",
            self._callback_overwrite_external_elevation_angle,
            is_checkable=True,
            tool_tip=(
                "Overwrite the external elevation angle, which might affect\n"
                "the LUT calculation. This is for the test purpose only."
            ),
        )

        self._button_apply_ilc = set_button(
            "Apply ILC Settings",
            self._callback_apply_ilc,
            tool_tip=("Apply the inner-loop controller (ILC) settings used in the\nstate transtion."),
        )

        self._button_apply_general = set_button("Apply General Settings", self._callback_apply_general)

        # Timer to write the external elevation angle continuously
        self._timer = self.create_and_start_timer(self._callback_time_out, self.model.duration_refresh)

        self.set_widget_and_layout()

        self._set_signal_config(self.model.signal_config)

    def _create_settings(self) -> dict:
        """Create the settings.

        Returns
        -------
        `dict`
            Settings.
        """

        settings = {
            "host": QLineEdit(),
            "port_command": QSpinBox(),
            "port_telemetry": QSpinBox(),
            "timeout_connection": QSpinBox(),
            "enable_lut_temperature": QCheckBox("Enable the temperature LUT"),
            "use_external_elevation_angle": QCheckBox("Use external elevation angle"),
            "enable_angle_comparison": QCheckBox("Enable angle comparison"),
            "max_angle_difference": QSpinBox(),
            "lut_temperature_ref": create_double_spin_box(
                "degree C",
                1,
                maximum=self.TEMPERATURE_REFERENCE_MAXIMUM,
                minimum=self.TEMPERATURE_REFERENCE_MINIMUM,
            ),
            "external_elevation_angle": create_double_spin_box(
                "degree",
                1,
                maximum=self.EXTERNAL_ELEVATION_ANGLE_MAXIMUM,
                minimum=self.EXTERNAL_ELEVATION_ANGLE_MINIMUM,
            ),
            "ilc_retry_times": QSpinBox(),
            "ilc_timeout": create_double_spin_box(
                "sec", 2, tool_tip="Timeout to transtion the ILC to Enabled state."
            ),
            "log_level": QSpinBox(),
            "refresh_frequency": QSpinBox(),
            "point_size": QSpinBox(),
        }

        for port in ("port_command", "port_telemetry"):
            settings[port].setRange(PORT_MINIMUM, PORT_MAXIMUM)

        settings["timeout_connection"].setMinimum(TIMEOUT_MINIMUM)
        settings["timeout_connection"].setSuffix(" sec")

        settings["enable_lut_temperature"].setToolTip(
            "Enable the calculation of temperature look-up table (LUT) or not."
        )
        settings["use_external_elevation_angle"].setToolTip(
            (
                "Use the external elevation angle such as MTMount\n"
                "to do the look-up table (LUT) calculation or not."
            )
        )
        settings["use_external_elevation_angle"].stateChanged.connect(
            self._callback_use_external_elevation_angle
        )

        settings["enable_angle_comparison"].setToolTip(
            (
                "Enable the comparison between the external and internal\n"
                "angles or not. If the external angle is used, this value\n"
                "will be True to protect the mirror."
            )
        )

        settings["max_angle_difference"].setToolTip(
            "Maximum allowed difference between the internal and external anlges."
        )

        settings["max_angle_difference"].setRange(
            self.ANGLE_DIFFERENCE_MINIMUM, self.ANGLE_DIFFERENCE_MAXIMUM
        )
        settings["max_angle_difference"].setSuffix(" degree")

        settings["ilc_retry_times"].setToolTip("Retry times to transtion the ILC to Enabled state.")

        settings["log_level"].setRange(LOG_LEVEL_MINIMUM, LOG_LEVEL_MAXIMUM)
        settings["log_level"].setToolTip("CRITICAL (50), ERROR (40), WARNING (30), INFO (20), DEBUG (10)")

        settings["refresh_frequency"].setRange(REFRESH_FREQUENCY_MINIMUM, REFRESH_FREQUENCY_MAXIMUM)
        settings["refresh_frequency"].setSuffix(" Hz")
        settings["refresh_frequency"].setToolTip("Frequency to refresh the data on tables")

        settings["point_size"].setRange(POINT_SIZE_MINIMUM, POINT_SIZE_MAXIMUM)
        settings["point_size"].setToolTip("Point size of the application.")

        # Set the default values
        controller = self.model.controller
        settings["host"].setText(controller.host)
        settings["port_command"].setValue(controller.port_command)
        settings["port_telemetry"].setValue(controller.port_telemetry)
        settings["timeout_connection"].setValue(controller.timeout_connection)

        settings["enable_lut_temperature"].setChecked(controller.control_parameters["enable_lut_temperature"])
        settings["use_external_elevation_angle"].setChecked(
            controller.control_parameters["use_external_elevation_angle"]
        )
        settings["enable_angle_comparison"].setChecked(
            controller.control_parameters["enable_angle_comparison"]
        )
        settings["max_angle_difference"].setValue(controller.control_parameters["max_angle_difference"])

        settings["ilc_retry_times"].setValue(self.model.ilc_retry_times)
        settings["ilc_timeout"].setValue(self.model.ilc_timeout)

        settings["log_level"].setValue(self.model.log.level)

        # The unit of self.model.duration_refresh is milliseconds
        frequency = int(1000 / self.model.duration_refresh)
        settings["refresh_frequency"].setValue(frequency)

        app = QApplication.instance()
        settings["point_size"].setValue(app.font().pointSize())

        self._set_minimum_width_line_edit(settings["host"])

        return settings

    @asyncSlot()
    async def _callback_use_external_elevation_angle(self, state: int) -> None:
        """Callback of the check box to use the external elevation angle.

        Parameters
        ----------
        state : `int`
            Check state.
        """

        check_box_enable_angle_comparison = self._settings["enable_angle_comparison"]

        check_state = Qt.CheckState(state)
        if check_state == Qt.CheckState.Unchecked:
            check_box_enable_angle_comparison.setEnabled(True)

        else:
            check_box_enable_angle_comparison.setChecked(True)
            check_box_enable_angle_comparison.setEnabled(False)

    def _set_minimum_width_line_edit(self, line_edit: QLineEdit, offset: int = 20) -> None:
        """Set the minimum width of line edit.

        Parameters
        ----------
        line_edit : `PySide6.QtWidgets.QLineEdit`
            Line edit.
        offset : `int`, optional
            Offset of the width. (the default is 20)
        """

        font_metrics = line_edit.fontMetrics()

        text = line_edit.text()
        width = font_metrics.boundingRect(text).width()
        line_edit.setMinimumWidth(width + offset)

    @asyncSlot()
    async def _callback_apply_host(self) -> None:
        """Callback of the apply-host-setting button. This will apply the
        new host settings to model."""

        host = self._settings["host"].text()
        port_command = self._settings["port_command"].value()
        port_telemetry = self._settings["port_telemetry"].value()
        timeout_connection = self._settings["timeout_connection"].value()

        await run_command(
            self.model.update_connection_information,
            host,
            port_command,
            port_telemetry,
            timeout_connection,
        )

    @asyncSlot()
    async def _callback_apply_control_parameters(self) -> None:
        """Callback of the apply-control-parameters button. The main target is
        to set the elevation angle used in the look-up table (LUT) calculation
        and decide to calculate the temperature LUT or not.
        """

        self.model.controller.control_parameters["enable_lut_temperature"] = self._settings[
            "enable_lut_temperature"
        ].isChecked()

        use_external_elevation_angle = self._settings["use_external_elevation_angle"].isChecked()
        max_angle_difference = self._settings["max_angle_difference"].value()
        enable_angle_comparison = self._settings["enable_angle_comparison"].isChecked()

        self.model.controller.select_inclination_source(
            use_external_elevation_angle=use_external_elevation_angle,
            max_angle_difference=max_angle_difference,
            enable_angle_comparison=enable_angle_comparison,
        )

    @asyncSlot()
    async def _callback_apply_temperature_reference(self) -> None:
        """Callback of apply-temperature-reference button. This will update the
        value used in the calculation of look-up table (LUT).
        """

        ref = self._settings["lut_temperature_ref"].value()
        await run_command(
            self.model.controller.set_temperature_offset,
            [ref] * NUM_TEMPERATURE_RING,
            [0.0] * NUM_TEMPERATURE_INTAKE,
            [0.0] * NUM_TEMPERATURE_EXHAUST,
        )

    @asyncSlot()
    async def _callback_overwrite_external_elevation_angle(self) -> None:
        """Callback of overwrite-external-elevation-angle button. This will
        overwrite the current external elevation angle in controller.
        """

        is_checked = self._button_overwrite_external_elevation_angle.isChecked()
        if is_checked:
            self.model.log.info("Overwrite the external elevation angle continuously.")
        else:
            self.model.log.info("Stop to overwrite the external elevation angle.")

    @asyncSlot()
    async def _callback_apply_ilc(self) -> None:
        """Callback of the apply-ilc-settings button. This will apply the
        new inner-loop controller (ILC) settings to model."""

        self.model.ilc_retry_times = int(self._settings["ilc_retry_times"].value())
        self.model.ilc_timeout = self._settings["ilc_timeout"].value()

    @asyncSlot()
    async def _callback_apply_general(self) -> None:
        """Callback of the apply-general-settings button. This will apply the
        new general settings to model."""

        self.model.log.setLevel(self._settings["log_level"].value())

        # The unit of self.model.duration_refresh is milliseconds
        self.model.duration_refresh = int(1000 / self._settings["refresh_frequency"].value())

        # Update the point size
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(self._settings["point_size"].value())
        app.setFont(font)

    @asyncSlot()
    async def _callback_time_out(self) -> None:
        """Callback timeout function to write the external elevation angle."""

        if self._button_overwrite_external_elevation_angle.isChecked():
            angle = self._settings["external_elevation_angle"].value()
            await run_command(self.model.controller.set_external_elevation_angle, angle)

        self.check_duration_and_restart_timer(self._timer, self.model.duration_refresh)

    def create_layout(self) -> QHBoxLayout:
        """Create the layout.

        Returns
        -------
        layout : `PySide6.QtWidgets.QHBoxLayout`
            Layout.
        """

        layout = QHBoxLayout()

        # First column
        layout_column_1 = QVBoxLayout()
        layout_column_1.addWidget(self._create_group_tcpip())
        layout_column_1.addWidget(self._create_group_control_parameters())
        layout_column_1.addWidget(self._create_group_lut_parameters())

        layout.addLayout(layout_column_1)

        # Second column
        layout_column_2 = QVBoxLayout()
        layout_column_2.addWidget(self._create_group_ilc_parameters())
        layout_column_2.addWidget(self._create_group_application())

        layout.addLayout(layout_column_2)

        return layout

    def _create_group_tcpip(self) -> QGroupBox:
        """Create the group of TCP/IP connection.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_tcpip = QFormLayout()
        layout_tcpip.addRow("Host name:", self._settings["host"])
        layout_tcpip.addRow("Commmand port:", self._settings["port_command"])
        layout_tcpip.addRow("Telemetry port:", self._settings["port_telemetry"])
        layout_tcpip.addRow("Connection timeout:", self._settings["timeout_connection"])

        layout.addLayout(layout_tcpip)
        layout.addWidget(self._button_apply_host)

        return create_group_box("Tcp/Ip Connection", layout)

    def _create_group_control_parameters(self) -> QGroupBox:
        """Create the group of control parameters.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_control = QFormLayout()
        layout_control.addRow(self._settings["enable_lut_temperature"])
        layout_control.addRow(self._settings["use_external_elevation_angle"])
        layout_control.addRow(self._settings["enable_angle_comparison"])
        layout_control.addRow("Maximum angle difference:", self._settings["max_angle_difference"])

        layout.addLayout(layout_control)
        layout.addWidget(self._button_apply_control_parameters)

        return create_group_box("Control Parameters", layout)

    def _create_group_lut_parameters(self) -> QGroupBox:
        """Create the group of look-up table (LUT) parameters.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_lut = QFormLayout()
        layout_lut.addRow("Temperature reference:", self._settings["lut_temperature_ref"])
        layout_lut.addRow("External elevation angle", self._settings["external_elevation_angle"])

        layout.addLayout(layout_lut)
        layout.addWidget(self._button_apply_temperature_reference)
        layout.addWidget(self._button_overwrite_external_elevation_angle)

        return create_group_box("Look-Up Table Parameters", layout)

    def _create_group_ilc_parameters(self) -> QGroupBox:
        """Create the group of inner-loop controller (ILC) parameters.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_ilc = QFormLayout()
        layout_ilc.addRow("Retry times:", self._settings["ilc_retry_times"])
        layout_ilc.addRow("Timeout:", self._settings["ilc_timeout"])

        layout.addLayout(layout_ilc)
        layout.addWidget(self._button_apply_ilc)

        return create_group_box("Inner-Loop Controller Parameters", layout)

    def _create_group_application(self) -> QGroupBox:
        """Create the group of application.

        Returns
        -------
        `PySide6.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        layout_app = QFormLayout()
        layout_app.addRow("Point size:", self._settings["point_size"])
        layout_app.addRow("Logging level:", self._settings["log_level"])
        layout_app.addRow("Refresh frequency:", self._settings["refresh_frequency"])

        layout.addLayout(layout_app)
        layout.addWidget(self._button_apply_general)

        return create_group_box("Application", layout)

    def _set_signal_config(self, signal_config: SignalConfig) -> None:
        """Set the config signal with callback function. This signal provides
        the temperature offset in the controller.

        Parameters
        ----------
        signal_config : `SignalConfig`
            Signal of the configuration.
        """

        signal_config.temperature_offset.connect(self._callback_signal_config_temperature_offset)

    @asyncSlot()
    async def _callback_signal_config_temperature_offset(self, temperature_offset: float) -> None:
        """Callback of the config signal for the temperature offset.

        Parameters
        ----------
        temperature_offset : `float`
            Temperature offset used in the look-up table calculation. The unit
            is degree C.
        """
        self._settings["lut_temperature_ref"].setValue(temperature_offset)
