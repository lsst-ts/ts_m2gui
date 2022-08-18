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

__all__ = ["TabUtilityView"]

from qasync import asyncSlot

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout, QFormLayout, QHBoxLayout
from PySide2.QtGui import QPalette

from lsst.ts.m2com import PowerType

from ..utils import set_button, create_label, create_group_box
from ..enums import TemperatureGroup, DisplacementSensorDirection
from . import TabDefault


class TabUtilityView(TabDefault):
    """Table of the utility view.

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

        # Utility data
        self._power_inclinometer = {
            "power_voltage_motor": create_label(),
            "power_current_motor": create_label(),
            "power_voltage_communication": create_label(),
            "power_current_communication": create_label(),
            "inclinometer": create_label(),
        }

        self._breakers = self._create_indicators_breaker()
        self._button_reset_breakers = set_button(
            "Reset Breakers", self._callback_reset_breakers
        )

        self._temperatures = self._create_labels_sensor_data(
            self.model.utility_monitor.temperatures
        )

        self._displacements = self._create_labels_sensor_data(
            self.model.utility_monitor.displacements
        )

        self._set_widget_and_layout()

        self._set_signal_utility(self.model.utility_monitor.signal_utility)

    def _create_indicators_breaker(self):
        """Create the indicators of breakers.

        Returns
        -------
        indicators : `dict [PySide2.QtWidgets.QPushButton]`
            Indicators of the breakers. The key is the breaker's name.
        """

        indicators = dict()
        for name in self.model.utility_monitor.breakers.keys():
            indicators[name] = set_button(
                name, None, is_indicator=True, is_adjust_size=True
            )
            self._update_indicator_color(indicators[name], False)

        return indicators

    def _update_indicator_color(self, indicator, is_fault):
        """Update the color of indicator.

        Parameters
        ----------
        indicator : `PySide2.QtWidgets.QPushButton`
            Indicator.
        is_fault : `bool`
            Is in fault or not.
        """

        palette = indicator.palette()

        if is_fault:
            palette.setColor(QPalette.Button, Qt.red)
        else:
            palette.setColor(QPalette.Button, Qt.green)

        indicator.setPalette(palette)

    @asyncSlot()
    async def _callback_reset_breakers(self):
        """Callback of the reset-breakers button. This will reset all triggered
        breakers."""
        self.model.utility_monitor.reset_breakers()

    def _create_labels_sensor_data(self, sensor_data):
        """Create the labels of sensor data.

        Parameters
        ----------
        sensor_data : `dict`
            Sensor data. The key is the sensor's name.

        Returns
        -------
        labels_sensor_data : `dict [PySide2.QtWidgets.QLabel]`
            Labels of the sensor data. The key is the sensor's name.
        """

        labels_sensor_data = dict()
        for sensor in sensor_data.keys():
            labels_sensor_data[sensor] = create_label()

        return labels_sensor_data

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
        layout_power_inclinometer = QVBoxLayout()
        layout_power_inclinometer.addWidget(self._create_group_power_motor())
        layout_power_inclinometer.addWidget(self._create_group_power_communication())
        layout_power_inclinometer.addWidget(self._create_group_inclinometer())

        layout.addLayout(layout_power_inclinometer)

        # Second column
        layout_breaker = QVBoxLayout()
        layout_breaker.addWidget(self._create_group_breakers(PowerType.Motor))
        layout_breaker.addWidget(self._create_group_breakers(PowerType.Communication))
        layout_breaker.addWidget(self._button_reset_breakers)

        layout.addLayout(layout_breaker)

        # Third column
        layout_temperature = QVBoxLayout()

        temperature_groups_cell = [TemperatureGroup.Intake, TemperatureGroup.Exhaust]
        group_title_cell = "Cell Internal Temperatures"
        layout_temperature.addWidget(
            self._create_group_temperatures(temperature_groups_cell, group_title_cell)
        )

        temperature_groups_mirror = [
            TemperatureGroup.LG2,
            TemperatureGroup.LG3,
            TemperatureGroup.LG4,
        ]
        group_title_mirror = "Mirror Temperatures"
        layout_temperature.addWidget(
            self._create_group_temperatures(
                temperature_groups_mirror, group_title_mirror
            )
        )

        layout.addLayout(layout_temperature)

        # Fourth column
        layout_displacement = QVBoxLayout()
        layout_displacement.addWidget(self._create_group_displacements())

        layout.addLayout(layout_displacement)

        return layout

    def _create_group_power_motor(self):
        """Create the group of motor power.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Voltage:", self._power_inclinometer["power_voltage_motor"])
        layout.addRow("Current:", self._power_inclinometer["power_current_motor"])

        return create_group_box("Motor Power", layout)

    def _create_group_power_communication(self):
        """Create the group of communication power.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow(
            "Voltage:", self._power_inclinometer["power_voltage_communication"]
        )
        layout.addRow(
            "Current:", self._power_inclinometer["power_current_communication"]
        )

        return create_group_box("Communication Power", layout)

    def _create_group_inclinometer(self):
        """Create the group of inclinometer.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        layout.addRow("Inclinometer Angle:", self._power_inclinometer["inclinometer"])

        return create_group_box("Elevation Angle", layout)

    def _create_group_breakers(self, power_type):
        """Create the group of breakers.

        Parameters
        ----------
        power_type : enum `lsst.ts.m2com.PowerType`
            Power type.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QVBoxLayout()

        breakers = self.model.utility_monitor.get_breakers(power_type)
        for breaker in breakers:
            layout.addWidget(self._breakers[breaker])

        return create_group_box(f"{power_type.name} Breakers", layout)

    def _create_group_temperatures(self, temperature_groups, group_title):
        """Create the group of temperature sensors.

        Parameters
        ----------
        temperature_groups : `list [TemperatureGroup]`
            List of the temperature groups.
        group_title : `str`
            Group title.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()
        for temperature_group in temperature_groups:
            sensors = self.model.utility_monitor.get_temperature_sensors(
                temperature_group
            )

            for sensor in sensors:
                layout.addRow(sensor + ":", self._temperatures[sensor])

            self.add_empty_row_to_form_layout(layout)

        return create_group_box(group_title, layout)

    def _create_group_displacements(self):
        """Create the group of displacement sensors.

        Returns
        -------
        group : `PySide2.QtWidgets.QGroupBox`
            Group.
        """

        layout = QFormLayout()

        sensors_theta = self.model.utility_monitor.get_displacement_sensors(
            DisplacementSensorDirection.Theta
        )
        sensors_delta = self.model.utility_monitor.get_displacement_sensors(
            DisplacementSensorDirection.Delta
        )

        for sensor_theta, sensor_delta in zip(sensors_theta, sensors_delta):
            layout.addRow(sensor_theta + ":", self._displacements[sensor_theta])
            layout.addRow(sensor_delta + ":", self._displacements[sensor_delta])
            self.add_empty_row_to_form_layout(layout)

        return create_group_box("Displacement Sensors", layout)

    def _set_signal_utility(self, signal_utility):
        """Set the utility signal with callback functions. This signal provides
        the utility status contains the power, inclinometer, breaker,
        temperature, displacements, etc.

        Parameters
        ----------
        signal_utility : `SignalUtility`
            Signal of the utility.
        """

        signal_utility.power_motor_calibrated.connect(self._callback_power_motor)
        signal_utility.power_communication_calibrated.connect(
            self._callback_power_communication
        )

        signal_utility.inclinometer.connect(self._callback_inclinometer)

        signal_utility.breaker_status.connect(self._callback_breakers)

        signal_utility.temperatures.connect(self._callback_temperatures)

        signal_utility.displacements.connect(self._callback_displacements)

    @asyncSlot()
    async def _callback_power_motor(self, power_motor):
        """Callback of the utility signal for the motor power.

        Parameters
        ----------
        power_motor : `tuple`
            Motor power: (voltage, current). The data type is float. The units
            are volt and ampere respectively.
        """

        self._power_inclinometer["power_voltage_motor"].setText(f"{power_motor[0]} V")
        self._power_inclinometer["power_current_motor"].setText(f"{power_motor[1]} A")

    @asyncSlot()
    async def _callback_power_communication(self, power_communication):
        """Callback of the utility signal for the communication power.

        Parameters
        ----------
        power_communication : `tuple`
            Communication power: (voltage, current). The data type is float.
            The units are volt and ampere respectively.
        """

        self._power_inclinometer["power_voltage_communication"].setText(
            f"{power_communication[0]} V"
        )
        self._power_inclinometer["power_current_communication"].setText(
            f"{power_communication[1]} A"
        )

    @asyncSlot()
    async def _callback_inclinometer(self, inclinometer):
        """Callback of the utility signal for the inclinometer angle.

        Parameters
        ----------
        inclinometer : `float`
            Inclinometer angle in degree.
        """
        self._power_inclinometer["inclinometer"].setText(f"{inclinometer} degree")

    @asyncSlot()
    async def _callback_breakers(self, breaker_status):
        """Callback of the utility signal for the breakers.

        Parameters
        ----------
        breaker_status : `tuple`
            Breaker status: (name, status). The data type of "name" is string,
            and the data type of "status" is bool. True if the breaker is
            triggered. Otherwise, False.
        """

        name = breaker_status[0]
        is_triggered = breaker_status[1]
        self._update_indicator_color(self._breakers[name], is_triggered)

    @asyncSlot()
    async def _callback_temperatures(self, temperatures):
        """Callback of the utility signal for the temperatures.

        Parameters
        ----------
        temperatures : `tuple`
            Temperatures: (temperature_group, [temperture_1, temperture_2, ...]
            ). The data type of "temperature_group" is the enum:
            `TemperatureGroup`. The data type of the temperature in
            "[temperture_1, temperture_2, ...]" is float. The unit is degree C.
            This list should have all the temperatures in the group.
        """

        temperature_group = temperatures[0]
        values = temperatures[1]

        sensors = self.model.utility_monitor.get_temperature_sensors(temperature_group)
        for sensor, value in zip(sensors, values):
            self._temperatures[sensor].setText(f"{value} degree C")

    @asyncSlot()
    async def _callback_displacements(self, displacements):
        """Callback of the utility signal for the displacements.

        Parameters
        ----------
        displacements : `tuple`
            Displacements: (sensor_direction, [displacement_1, displacement_2,
            ...]). The data type of "sensor_direction" is the enum:
            `DisplacementSensorDirection`. The data type of displacement in
            "[displacement_1, displacement_2, ...]" is float. The unit is mm.
            This list should have all the displacements in the direction.
        """

        sensor_direction = displacements[0]
        values = displacements[1]

        sensors = self.model.utility_monitor.get_displacement_sensors(sensor_direction)
        for sensor, value in zip(sensors, values):
            self._displacements[sensor].setText(f"{value} mm")
