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

__all__ = ["UtilityMonitor"]

import re
import numpy as np
from copy import deepcopy

from . import (
    ActuatorForce,
    ForceErrorTangent,
    SignalUtility,
    SignalDetailedForce,
    SignalPosition,
    PowerType,
    TemperatureGroup,
    DisplacementSensorDirection,
    get_tol,
)


class UtilityMonitor(object):
    """Utility monitor to monitor the utility status.

    Attributes
    ----------
    signal_utility : `SignalUtility`
        Signal to report the utility status.
    signal_detailed_force : `SignalDetailedForce`
        Signal to report the detailed force.
    signal_position : `SignalPosition`
        Signal to report the rigid body position.
    power_motor_calibrated : `dict`
        Calibrated motor power. The unit of voltage is volt and the unit of
        current is ampere.
    power_communication_calibrated : `dict`
        Calibrated communication power. The unit of voltage is volt and the
        unit of current is ampere.
    power_motor_raw : `dict`
        Raw motor power. The unit of voltage is volt and the unit of current is
        ampere.
    power_communication_raw : `dict`
        Raw communication power. The unit of voltage is volt and the unit of
        current is ampere.
    inclinometer_angle : `float`
        Inclinometer angle in degree.
    breakers : `dict`
        Breakers. The key is the breaker name. If the breaker is triggered, the
        value is True. Otherwise, False.
    temperatures : `dict`
        Tempertures. The key is the temperature sensor name. The value is the
        related temperature in degree C.
    displacements : `dict`
        Displacement sensors. The key is the displacement sensor name. The
        value is the reading in the unit of mm.
    digital_status_input : `int`
        Digital input status as a 32 bits value. Each bit means different
        status. 1 means OK (or triggered). Otherwise 0.
    digital_status_output : `int`
        Digital output status as a 8 bits value. Each bit means different
        status. 1 means OK (or triggered). Otherwise 0.
    hard_points : `dict`
        Hard points of the axial and tangential actuators.
    forces : `ActuatorForce`
        Detailed actuator forces.
    force_error_tangent : `ForceErrorTangent`
        Tangential force error to monitor the supporting force of mirror.
    position : `list`
        Rigid body position: [x, y, z, rx, ry, rz]. The unit of x, y, and z is
        um. The unit of rx, ry, and ry is arcsec.
    """

    # Number of digits after the decimal
    # It is meaningless to have a high accurate value such as x.xxxx shown on
    # the graphical user interface (GUI) at the most of time. In addition, the
    # high-frequent update of GUI might drain the limited computer resource.
    NUM_DIGIT_AFTER_DECIMAL = 1

    # Number of digits after the decimal for the displacement sensors
    NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT = 3

    def __init__(self):

        self.signal_utility = SignalUtility()
        self.signal_detailed_force = SignalDetailedForce()
        self.signal_position = SignalPosition()

        self.power_motor_calibrated = self._get_default_power()
        self.power_communication_calibrated = self._get_default_power()

        self.power_motor_raw = self._get_default_power()
        self.power_communication_raw = self._get_default_power()

        self.inclinometer_angle = 0

        self.breakers = {
            "J1-W9-1": False,
            "J1-W9-2": False,
            "J1-W9-3": False,
            "J2-W10-1": False,
            "J2-W10-2": False,
            "J2-W10-3": False,
            "J3-W11-1": False,
            "J3-W11-2": False,
            "J3-W11-3": False,
            "J1-W12-1": False,
            "J1-W12-2": False,
            "J2-W13-1": False,
            "J2-W13-2": False,
            "J3-W14-1": False,
            "J3-W14-2": False,
        }

        self.temperatures = {
            "Intake-1": 0,
            "Intake-2": 0,
            "Exhaust-1": 0,
            "Exhaust-2": 0,
            "LG2-1": 0,
            "LG2-2": 0,
            "LG2-3": 0,
            "LG2-4": 0,
            "LG3-1": 0,
            "LG3-2": 0,
            "LG3-3": 0,
            "LG3-4": 0,
            "LG4-1": 0,
            "LG4-2": 0,
            "LG4-3": 0,
            "LG4-4": 0,
        }

        self.displacements = {
            "A1-Theta_z": 0,
            "A2-Theta_z": 0,
            "A3-Theta_z": 0,
            "A4-Theta_z": 0,
            "A5-Theta_z": 0,
            "A6-Theta_z": 0,
            "A1-Delta_z": 0,
            "A2-Delta_z": 0,
            "A3-Delta_z": 0,
            "A4-Delta_z": 0,
            "A5-Delta_z": 0,
            "A6-Delta_z": 0,
        }

        self.digital_status_input = 0
        self.digital_status_output = 0

        self.hard_points = {"axial": [0, 0, 0], "tangent": [0, 0, 0]}

        self.forces = ActuatorForce()
        self.force_error_tangent = ForceErrorTangent()

        self.position = [0, 0, 0, 0, 0, 0]

    def _get_default_power(self):
        """Get the default power data.

        Returns
        -------
        `dict`
            Default power data. The unit of voltage is volt and the unit of
            current is ampere.
        """

        return {"voltage": 0, "current": 0}

    def report_utility_status(self):
        """Report the utility status."""

        self._report_powers()

        self.signal_utility.inclinometer.emit(self.inclinometer_angle)

        for name, status in self.breakers.items():
            self.signal_utility.breaker_status.emit((name, status))

        self._report_temperatures()
        self._report_displacements()
        self._report_digital_status()

        self._report_forces()

        self.signal_position.position.emit(self.position)

    def _report_powers(self):
        """Report the powers."""

        self.signal_utility.power_motor_calibrated.emit(
            tuple(self.power_motor_calibrated.values())
        )
        self.signal_utility.power_communication_calibrated.emit(
            tuple(self.power_communication_calibrated.values())
        )

        self.signal_utility.power_motor_raw.emit(tuple(self.power_motor_raw.values()))
        self.signal_utility.power_communication_raw.emit(
            tuple(self.power_communication_raw.values())
        )

    def _report_temperatures(self):
        """Report the temperatures."""

        for temperature_group in TemperatureGroup:
            sensors = self.get_temperature_sensors(temperature_group)

            temperatures = list()
            for sensor in sensors:
                temperatures.append(self.temperatures[sensor])

            self.signal_utility.temperatures.emit((temperature_group, temperatures))

    def _report_displacements(self):
        """Report the displacements."""

        for direction in DisplacementSensorDirection:
            sensors = self.get_displacement_sensors(direction)
            displacements = [self.displacements[sensor] for sensor in sensors]

            self.signal_utility.displacements.emit((direction, displacements))

    def _report_digital_status(self):
        """Report the digital input/output status."""

        self.signal_utility.digital_status_input.emit(self.digital_status_input)
        self.signal_utility.digital_status_output.emit(self.digital_status_output)

    def _report_forces(self):
        """Report the forces."""

        self.signal_detailed_force.hard_points.emit(
            self.hard_points["axial"] + self.hard_points["tangent"]
        )
        self.signal_detailed_force.forces.emit(self.forces)
        self.signal_detailed_force.force_error_tangent.emit(self.force_error_tangent)

    def get_temperature_sensors(self, temperature_group):
        """Get the temperature sensors in a specific group.

        Parameters
        ----------
        temperature_group : enum `TemperatureGroup`
            Temperature group.

        Returns
        -------
        `list [str]`
            List of the sensors.
        """

        sensors = list()
        for sensor in list(self.temperatures.keys()):
            if sensor.startswith(temperature_group.name):
                sensors.append(sensor)

        return sensors

    def get_displacement_sensors(self, direction):
        """Get the displacement sensors in a specific direction.

        Parameters
        ----------
        direction : enum `DisplacementSensorDirection`
            Direction of the displacement sensors.

        Returns
        -------
        `list [str]`
            List of the sensors.
        """

        sensors = []
        for sensor in self.displacements.keys():
            result = re.match(rf"\AA\d-{direction.name}_z", sensor)
            if result is not None:
                sensors.append(result.group())

        return sensors

    def update_power_calibrated(self, power_type, new_voltage, new_current):
        """Update the calibrated power data.

        Parameters
        ----------
        power_type : enum `PowerType`
            Power type.
        new_voltage : `float`
            New voltage value in volt.
        new_current : `float`
            New current value in ampere.

        Raises
        ------
        `ValueError`
            Not supported power type.
        """

        if power_type == PowerType.Motor:
            power = self.power_motor_calibrated
            signal_name = "power_motor_calibrated"
        elif power_type == PowerType.Communication:
            power = self.power_communication_calibrated
            signal_name = "power_communication_calibrated"
        else:
            raise ValueError(f"Not supported power type: {power_type!r}.")

        self._update_power(power, new_voltage, new_current, signal_name)

    def _update_power(self, power, new_voltage, new_current, signal_name):
        """Update the power data.

        Parameters
        ----------
        power : `dict`
            Power data.
        new_voltage : `float`
            New voltage value in volt.
        new_current : `float`
            New current value in ampere.
        signal_name : `str`
            Name of the signal.
        """

        tol = get_tol(self.NUM_DIGIT_AFTER_DECIMAL)
        if self._has_changed(power["voltage"], new_voltage, tol) or self._has_changed(
            power["current"], new_current, tol
        ):

            power["voltage"] = round(new_voltage, self.NUM_DIGIT_AFTER_DECIMAL)
            power["current"] = round(new_current, self.NUM_DIGIT_AFTER_DECIMAL)

            getattr(self.signal_utility, signal_name).emit(
                (power["voltage"], power["current"])
            )

    def _has_changed(self, value_old, value_new, tol):
        """The value has changed or not based on the tolerance.

        If the input values are arrays, compare the maximum change in arrays
        with the tolerance.

        Parameters
        ----------
        value_old : `float` or `numpy.ndarray`
            Old value.
        value_new : `float` or `numpy.ndarray`
            New value. The data type should be the same as the "value_old".
        tol : `float`
            tolerance.

        Returns
        -------
        `bool`
            True if the value is changed. Otherwise, False.
        """

        return np.max(np.abs(value_old - value_new)) >= tol

    def update_power_raw(self, power_type, new_voltage, new_current):
        """Update the raw power data.

        Parameters
        ----------
        power_type : enum `PowerType`
            Power type.
        new_voltage : `float`
            New voltage value in volt.
        new_current : `float`
            New current value in ampere.

        Raises
        ------
        `ValueError`
            Not supported power type.
        """

        if power_type == PowerType.Motor:
            power = self.power_motor_raw
            signal_name = "power_motor_raw"
        elif power_type == PowerType.Communication:
            power = self.power_communication_raw
            signal_name = "power_communication_raw"
        else:
            raise ValueError(f"Not supported power type: {power_type!r}.")

        self._update_power(power, new_voltage, new_current, signal_name)

    def update_inclinometer_angle(self, new_angle):
        """Update the angle of inclinometer.

        Parameters
        ----------
        new_angle : `float`
            New angle value in degree.
        """

        tol = get_tol(self.NUM_DIGIT_AFTER_DECIMAL)
        if self._has_changed(self.inclinometer_angle, new_angle, tol):
            self.inclinometer_angle = round(new_angle, self.NUM_DIGIT_AFTER_DECIMAL)
            self.signal_utility.inclinometer.emit(self.inclinometer_angle)

    def update_breaker(self, name, new_status):
        """Update the breaker status.

        Parameters
        ----------
        name : `str`
            Breaker name, which is in the keys of self.breakers.
        new_status : `float`
            New status of breaker. If the breake is triggered, put True,
            otherwise, False.
        """

        if self.breakers[name] is not new_status:
            self.breakers[name] = new_status
            self.signal_utility.breaker_status.emit((name, new_status))

    def reset_breakers(self):
        """Reset the breakers."""

        for name in self.breakers.keys():
            self.update_breaker(name, False)

    def get_breakers(self, power_type):
        """Get the breakers of the specific power type.

        Parameters
        ----------
        power_type : enum `PowerType`
            Power type.

        Returns
        -------
        `list [str]`
            List of the breakers.
        """

        if power_type == PowerType.Motor:
            breaker_range = range(9, 12)
        else:
            breaker_range = range(12, 15)

        breakers = list()
        for breaker in self.breakers.keys():
            result = re.match(r"\AJ\d-W(\d+)-\d", breaker)
            value = int(result.groups()[0])

            if value in breaker_range:
                breakers.append(breaker)

        return breakers

    def update_temperature(self, temperature_group, new_temperatures):
        """Update the temperature data.

        This function assumes the temperature's fluctuation is usually
        restricted to a small region (group) in the most of time.

        Parameters
        ----------
        temperature_group : enum `TemperatureGroup`
            Temperature group.
        new_temperatures : `list [float]`
            New temperatures in degree. The order should begin from sensor 1 to
            sensor n defined in the specific temperature group.
        """

        sensors = self.get_temperature_sensors(temperature_group)
        self._update_sensors(
            sensors,
            new_temperatures,
            self.NUM_DIGIT_AFTER_DECIMAL,
            self.temperatures,
            self.signal_utility.temperatures,
            temperature_group,
        )

    def _update_sensors(
        self, sensors, new_values, num_digit_after_decimal, data, signal, signal_item
    ):
        """Update the sensor data.

        Parameters
        ----------
        sensors : `list [str]`
            List of the sensor names.
        new_values : `list [float]`
            List of the new values. The size should be the same as the
            "sensors".
        num_digit_after_decimal : `int`
            Number of digits after the decimal. This should be greater than 0.
        data : `dict`
            Sensor data.
        signal : `PySide2.QtCore.Signal`
            Signal in QT framework.
        signal_item :
            Item used in the signal's message.

        Raises
        ------
        `ValueError`
            The size of sensors does not match with the size of values.
        """

        size_sensors = len(sensors)
        size_values = len(new_values)
        if size_sensors != size_values:
            raise ValueError(
                f"Size of sensors (={size_sensors}) != size of values (={size_values})."
            )

        tol = get_tol(num_digit_after_decimal)

        is_update_required = False
        for sensor, new_value in zip(sensors, new_values):
            if self._has_changed(data[sensor], new_value, tol):
                is_update_required = True
                break

        if is_update_required:
            values_updated = list()
            for sensor, new_value in zip(sensors, new_values):
                data[sensor] = round(new_value, num_digit_after_decimal)
                values_updated.append(data[sensor])

            signal.emit((signal_item, values_updated))

    def update_displacements(self, direction, new_displacements):
        """Update the displacement sensor data.

        This function assumes the mirror's movement is usually in a specific
        direction.

        Parameters
        ----------
        direction : enum `DisplacementSensorDirection`
            Direction of the displacement sensors.
        new_displacements : `list [float]`
            New displacements in millimeter. The order should begin from sensor
            1 to sensor n defined in the specific direction.
        """

        sensors = self.get_displacement_sensors(direction)
        self._update_sensors(
            sensors,
            new_displacements,
            self.NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT,
            self.displacements,
            self.signal_utility.displacements,
            direction,
        )

    def update_digital_status_input(self, new_status):
        """Update the digital input status (32 bits).

        Parameters
        ----------
        new_status : `int`
            New status.
        """

        if self.digital_status_input != new_status:
            self.digital_status_input = int(new_status)
            self.signal_utility.digital_status_input.emit(self.digital_status_input)

    def update_digital_status_output(self, new_status):
        """Update the digital output status (8 bits).

        Parameters
        ----------
        new_status : `int`
            New status.
        """

        if self.digital_status_output != new_status:
            self.digital_status_output = int(new_status)
            self.signal_utility.digital_status_output.emit(self.digital_status_output)

    def update_hard_points(self, axial, tangent):
        """Update the hard points.

        Parameters
        ----------
        axial : `list`
            List of the hard points in axial direction.
        tangent : `list`
            List of the hard points in tangent direction.

        Raises
        ------
        `ValueError`
            Lengths of the inputs are not right.
        """

        length_axial = len(self.hard_points["axial"])
        length_tangent = len(self.hard_points["tangent"])
        if len(axial) != length_axial or len(tangent) != length_tangent:
            raise ValueError(
                f"Length should be (axial, tangent) = ({length_axial}, {length_tangent})."
            )

        self.hard_points["axial"] = axial
        self.hard_points["tangent"] = tangent

        self.signal_detailed_force.hard_points.emit(
            self.hard_points["axial"] + self.hard_points["tangent"]
        )

    def update_forces(self, actuator_force):
        """Update the forces.

        Parameters
        ----------
        actuator_force : `ActuatorForce`
            Actuator force.
        """

        tol = get_tol(self.NUM_DIGIT_AFTER_DECIMAL)
        if self._has_changed(
            np.array(self.forces.f_cur), np.array(actuator_force.f_cur), tol
        ) or self._has_changed(
            np.array(self.forces.position_in_mm),
            np.array(actuator_force.position_in_mm),
            tol,
        ):
            # Use the deepcopy() here to make sure the above comparison can
            # always work
            self.forces = deepcopy(actuator_force)
            self.signal_detailed_force.forces.emit(self.forces)

    def update_force_error_tangent(self, force_error_tangent):
        """Update the tangential force error that monitors the supporting
        force of mirror.

        Parameters
        ----------
        force_error_tangent : `ForceErrorTangent`
            Tangential force error.
        """

        num_digit_after_decimal = self.NUM_DIGIT_AFTER_DECIMAL
        tol = get_tol(num_digit_after_decimal)
        if self._has_changed(
            self.force_error_tangent.error_weight, force_error_tangent.error_weight, tol
        ) or self._has_changed(
            self.force_error_tangent.error_sum,
            force_error_tangent.error_sum,
            tol,
        ):
            self.force_error_tangent.error_force = [
                round(force, num_digit_after_decimal)
                for force in force_error_tangent.error_force
            ]
            self.force_error_tangent.error_weight = round(
                force_error_tangent.error_weight, num_digit_after_decimal
            )
            self.force_error_tangent.error_sum = round(
                force_error_tangent.error_sum, num_digit_after_decimal
            )

            self.signal_detailed_force.force_error_tangent.emit(
                self.force_error_tangent
            )

    def update_position(self, x, y, z, rx, ry, rz):
        """Update the position of rigid body.

        Parameters
        ----------
        x : `float`
            Position x in um.
        y : `float`
            Position y in um.
        z : `float`
            Position z in um.
        rx : `float`
            Rotation x in arcsec.
        ry : `float`
            Rotation y in arcsec.
        rz : `float`
            Rotation z in arcsec.
        """

        tol = get_tol(self.NUM_DIGIT_AFTER_DECIMAL)

        is_changed = False
        components = [x, y, z, rx, ry, rz]
        for idx, component in enumerate(components):
            if self._has_changed(self.position[idx], component, tol):
                is_changed = True
                break

        if is_changed:
            for idx, component in enumerate(components):
                self.position[idx] = round(component, self.NUM_DIGIT_AFTER_DECIMAL)

            self.signal_position.position.emit(self.position)
