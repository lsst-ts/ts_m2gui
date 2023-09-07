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

__all__ = ["UtilityMonitor"]

import re
import typing
from copy import deepcopy

import numpy as np
import numpy.typing
from lsst.ts.idl.enums import MTM2
from lsst.ts.m2com import DigitalInput
from PySide2.QtCore import Signal

from .actuator_force_axial import ActuatorForceAxial
from .actuator_force_tangent import ActuatorForceTangent
from .enums import DisplacementSensorDirection, TemperatureGroup
from .force_error_tangent import ForceErrorTangent
from .signals import (
    SignalDetailedForce,
    SignalNetForceMoment,
    SignalPosition,
    SignalUtility,
)
from .utils import get_tol


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
    signal_net_force_moment : `SignalNetForceMoment`
        Signal to send the net force, moment, and force balance status.
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
    inclinometer_angle_tma : `float`
        Inclinometer angle of telescope mount assembly (TMA) in degree.
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
    forces_axial : `ActuatorForceAxial`
        Detailed axial actuator forces.
    forces_tangent : `ActuatorForceTangent`
        Detailed tangent actuator forces.
    force_error_tangent : `ForceErrorTangent`
        Tangential force error to monitor the supporting force of mirror.
    position : `list`
        Rigid body position: [x, y, z, rx, ry, rz] based on the hardpoint
        displacement. The unit of x, y, and z is um. The unit of rx, ry, and
        ry is arcsec.
    position_ims : `list`
        Rigid body position: [x, y, z, rx, ry, rz] based on the independent
        measurement system (IMS). The unit of x, y, and z is um. The unit of
        rx, ry, and ry is arcsec.
    net_force_total : `list`
        Total actuator net force in Newton: [fx, fy, fz].
    net_moment_total : `list`
        Total actuator net moment in Newton * meter: [mx, my, mz].
    force_balance : `list`
        Force balance status: [fx, fy, fz, mx, my, mz]. The units of force and
        moment are Newton and Newton * meter.
    """

    # Number of digits after the decimal
    # It is meaningless to have a high accurate value such as x.xxxx shown on
    # the graphical user interface (GUI) at the most of time. In addition, the
    # high-frequent update of GUI might drain the limited computer resource.
    NUM_DIGIT_AFTER_DECIMAL = 1

    # Number of digits after the decimal for the displacement sensors
    NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT = 3

    def __init__(self) -> None:
        self.signal_utility = SignalUtility()
        self.signal_detailed_force = SignalDetailedForce()
        self.signal_position = SignalPosition()
        self.signal_net_force_moment = SignalNetForceMoment()

        self.power_motor_calibrated = self._get_default_power()
        self.power_communication_calibrated = self._get_default_power()

        self.power_motor_raw = self._get_default_power()
        self.power_communication_raw = self._get_default_power()

        self.inclinometer_angle = 0.0
        self.inclinometer_angle_tma = 0.0

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

        self.forces_axial = ActuatorForceAxial()
        self.forces_tangent = ActuatorForceTangent()

        self.force_error_tangent = ForceErrorTangent()

        self.position = [0.0] * 6
        self.position_ims = [0.0] * 6

        self.net_force_total = [0.0] * 3
        self.net_moment_total = [0.0] * 3

        self.force_balance = [0.0] * 6

    def _get_default_power(self) -> dict:
        """Get the default power data.

        Returns
        -------
        `dict`
            Default power data. The unit of voltage is volt and the unit of
            current is ampere.
        """

        return {"voltage": 0, "current": 0}

    def get_forces_axial(self) -> ActuatorForceAxial:
        """Get the axial forces.

        Returns
        -------
        `ActuatorForceAxial`
            Detailed axial actuator forces as a new copy of internal data.
        """
        return deepcopy(self.forces_axial)

    def get_forces_tangent(self) -> ActuatorForceTangent:
        """Get the tangent forces.

        Returns
        -------
        `ActuatorForceTangent`
            Detailed tangent actuator forces as a new copy of internal data.
        """
        return deepcopy(self.forces_tangent)

    def report_utility_status(self) -> None:
        """Report the utility status."""

        self._report_powers()

        self.signal_utility.inclinometer_raw.emit(self.inclinometer_angle)
        self.signal_utility.inclinometer_processed.emit(self.inclinometer_angle)
        self.signal_utility.inclinometer_tma.emit(self.inclinometer_angle_tma)

        for name, status in self.breakers.items():
            self.signal_utility.breaker_status.emit((name, status))

        self._report_temperatures()
        self._report_displacements()
        self._report_digital_status()

        self._report_forces()

        self.signal_position.position.emit(self.position)
        self.signal_position.position_ims.emit(self.position_ims)

        self._report_net_force_moment_force_balance()

    def _report_powers(self) -> None:
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

    def _report_temperatures(self) -> None:
        """Report the temperatures."""

        for temperature_group in TemperatureGroup:
            sensors = self.get_temperature_sensors(temperature_group)

            temperatures = list()
            for sensor in sensors:
                temperatures.append(self.temperatures[sensor])

            self.signal_utility.temperatures.emit((temperature_group, temperatures))

    def _report_displacements(self) -> None:
        """Report the displacements."""

        for direction in DisplacementSensorDirection:
            sensors = self.get_displacement_sensors(direction)
            displacements = [self.displacements[sensor] for sensor in sensors]

            self.signal_utility.displacements.emit((direction, displacements))

    def _report_digital_status(self) -> None:
        """Report the digital input/output status."""

        self.signal_utility.digital_status_input.emit(self.digital_status_input)
        self.signal_utility.digital_status_output.emit(self.digital_status_output)

    def _report_forces(self) -> None:
        """Report the forces."""

        self.signal_detailed_force.hard_points.emit(
            self.hard_points["axial"] + self.hard_points["tangent"]
        )
        self.signal_detailed_force.forces_axial.emit(self.forces_axial)
        self.signal_detailed_force.forces_tangent.emit(self.forces_tangent)
        self.signal_detailed_force.force_error_tangent.emit(self.force_error_tangent)

    def _report_net_force_moment_force_balance(self) -> None:
        """Report the total net force, moment, and force balance status."""

        self.signal_net_force_moment.net_force_total.emit(self.net_force_total)
        self.signal_net_force_moment.net_moment_total.emit(self.net_moment_total)

        self.signal_net_force_moment.force_balance.emit(self.force_balance)

    def get_temperature_sensors(self, temperature_group: TemperatureGroup) -> list[str]:
        """Get the temperature sensors in a specific group.

        Parameters
        ----------
        temperature_group : enum `TemperatureGroup`
            Temperature group.

        Returns
        -------
        `list` [`str`]
            List of the sensors.
        """

        sensors = list()
        for sensor in list(self.temperatures.keys()):
            if sensor.startswith(temperature_group.name):
                sensors.append(sensor)

        return sensors

    def get_displacement_sensors(
        self, direction: DisplacementSensorDirection
    ) -> list[str]:
        """Get the displacement sensors in a specific direction.

        Parameters
        ----------
        direction : enum `DisplacementSensorDirection`
            Direction of the displacement sensors.

        Returns
        -------
        `list` [`str`]
            List of the sensors.
        """

        sensors = list()
        for sensor in self.displacements.keys():
            result = re.match(rf"\AA\d-{direction.name}_z", sensor)
            if result is not None:
                sensors.append(result.group())

        return sensors

    def update_power_calibrated(
        self, power_type: MTM2.PowerType, new_voltage: float, new_current: float
    ) -> None:
        """Update the calibrated power data.

        Parameters
        ----------
        power_type : enum `MTM2.PowerType`
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

        if power_type == MTM2.PowerType.Motor:
            power = self.power_motor_calibrated
            signal_name = "power_motor_calibrated"
        elif power_type == MTM2.PowerType.Communication:
            power = self.power_communication_calibrated
            signal_name = "power_communication_calibrated"
        else:
            raise ValueError(f"Not supported power type: {power_type!r}.")

        self._update_power(power, new_voltage, new_current, signal_name)

    def _update_power(
        self, power: dict, new_voltage: float, new_current: float, signal_name: str
    ) -> None:
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

    def _has_changed(
        self,
        value_old: float | numpy.typing.NDArray[np.float64],
        value_new: float | numpy.typing.NDArray[np.float64],
        tol: float,
    ) -> bool:
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

    def update_power_raw(
        self, power_type: MTM2.PowerType, new_voltage: float, new_current: float
    ) -> None:
        """Update the raw power data.

        Parameters
        ----------
        power_type : enum `MTM2.PowerType`
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

        if power_type == MTM2.PowerType.Motor:
            power = self.power_motor_raw
            signal_name = "power_motor_raw"
        elif power_type == MTM2.PowerType.Communication:
            power = self.power_communication_raw
            signal_name = "power_communication_raw"
        else:
            raise ValueError(f"Not supported power type: {power_type!r}.")

        self._update_power(power, new_voltage, new_current, signal_name)

    def update_inclinometer_angle(
        self,
        new_angle: float,
        new_angle_processed: float | None = None,
        is_internal: bool = True,
    ) -> None:
        """Update the angle of inclinometer.

        Parameters
        ----------
        new_angle : `float`
            New angle value in degree.
        new_angle_processed : `float` or None, optional
            New processed angle value in degree.
        is_internal : `bool`
            Is the internal inclinometer or not. If False, the new_angle comes
            from the telescope mount assembly (TMA). (the default is True)
        """

        original_angle = (
            self.inclinometer_angle if is_internal else self.inclinometer_angle_tma
        )
        signal = (
            self.signal_utility.inclinometer_raw
            if is_internal
            else self.signal_utility.inclinometer_tma
        )

        tol = get_tol(self.NUM_DIGIT_AFTER_DECIMAL)
        if self._has_changed(original_angle, new_angle, tol):
            angle_rounded = round(new_angle, self.NUM_DIGIT_AFTER_DECIMAL)
            signal.emit(angle_rounded)

            if is_internal and (new_angle_processed is not None):
                self.signal_utility.inclinometer_processed.emit(
                    round(new_angle_processed, self.NUM_DIGIT_AFTER_DECIMAL)
                )

            if is_internal:
                self.inclinometer_angle = angle_rounded
            else:
                self.inclinometer_angle_tma = angle_rounded

    def update_breaker(self, name: str, new_status: bool) -> None:
        """Update the breaker status.

        Parameters
        ----------
        name : `str`
            Breaker name, which is in the keys of self.breakers.
        new_status : `bool`
            New status of breaker. If the breake is triggered, put True,
            otherwise, False.
        """

        if self.breakers[name] is not new_status:
            self.breakers[name] = new_status
            self.signal_utility.breaker_status.emit((name, new_status))

    def reset_breakers(self, power_type: MTM2.PowerType) -> None:
        """Reset the breakers.

        Parameters
        ----------
        power_type : enum `MTM2.PowerType`
            Power type.
        """

        breakers = self.get_breakers(power_type)
        for breaker in breakers:
            self.update_breaker(breaker, False)

    def get_breakers(self, power_type: MTM2.PowerType) -> list[str]:
        """Get the breakers of the specific power type.

        Parameters
        ----------
        power_type : enum `MTM2.PowerType`
            Power type.

        Returns
        -------
        `list` [`str`]
            List of the breakers.
        """

        if power_type == MTM2.PowerType.Motor:
            breaker_range = range(9, 12)
        else:
            breaker_range = range(12, 15)

        breakers = list()
        for breaker in self.breakers.keys():
            result = re.match(r"\AJ\d-W(\d+)-\d", breaker)

            # Workaround of the mypy checking
            assert result is not None

            value = int(result.groups()[0])

            if value in breaker_range:
                breakers.append(breaker)

        return breakers

    def update_temperature(
        self, temperature_group: TemperatureGroup, new_temperatures: list[float]
    ) -> None:
        """Update the temperature data.

        This function assumes the temperature's fluctuation is usually
        restricted to a small region (group) in the most of time.

        Parameters
        ----------
        temperature_group : enum `TemperatureGroup`
            Temperature group.
        new_temperatures : `list` [`float`]
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
        self,
        sensors: list[str],
        new_values: list[float],
        num_digit_after_decimal: int,
        data: dict,
        signal: Signal,
        signal_item: typing.Any,
    ) -> None:
        """Update the sensor data.

        Parameters
        ----------
        sensors : `list` [`str`]
            List of the sensor names.
        new_values : `list` [`float`]
            List of the new values. The size should be the same as the
            "sensors".
        num_digit_after_decimal : `int`
            Number of digits after the decimal. This should be greater than 0.
        data : `dict`
            Sensor data.
        signal : `PySide2.QtCore.Signal`
            Signal in QT framework.
        signal_item : `any`
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

    def update_displacements(
        self,
        direction: DisplacementSensorDirection,
        new_displacements: list[float],
    ) -> None:
        """Update the displacement sensor data.

        This function assumes the mirror's movement is usually in a specific
        direction.

        Parameters
        ----------
        direction : enum `DisplacementSensorDirection`
            Direction of the displacement sensors.
        new_displacements : `list` [`float`]
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

    def update_digital_status_input(self, new_status: int) -> None:
        """Update the digital input status (32 bits).

        Parameters
        ----------
        new_status : `int`
            New status.
        """

        if self.digital_status_input != new_status:
            self.digital_status_input = int(new_status)

            value_update = self._process_digital_status_input(new_status)
            self.signal_utility.digital_status_input.emit(value_update)

    def _process_digital_status_input(self, value: int) -> int:
        """Process the digital input status.

        This is based on the Model.processPowerStatusTelemetry.vi in ts_mtm2.

        Parameters
        ----------
        value : `int`
            Value.

        Returns
        -------
        value_update : `int`
            Updated value.
        """

        value_update = value
        for item in DigitalInput:
            if ("PowerBreaker" in item.name) or ("PowerRelay" in item.name):
                value_update = value_update ^ item.value

        return value_update

    def update_digital_status_output(self, new_status: int) -> None:
        """Update the digital output status (8 bits).

        Parameters
        ----------
        new_status : `int`
            New status.
        """

        if self.digital_status_output != new_status:
            self.digital_status_output = int(new_status)
            self.signal_utility.digital_status_output.emit(self.digital_status_output)

    def update_hard_points(self, axial: list[int], tangent: list[int]) -> None:
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

    def update_forces_axial(self, actuator_force: ActuatorForceAxial) -> None:
        """Update the axial actuator forces.

        Parameters
        ----------
        actuator_force : `ActuatorForceAxial`
            Axial actuator force.

        Raises
        ------
        `ValueError`
            When the input is the same object of self.forces_axial.
        """

        if id(actuator_force) == id(self.forces_axial):
            raise ValueError("Input cannot be the same object of self.forces_axial.")

        self.forces_axial = actuator_force
        self.signal_detailed_force.forces_axial.emit(self.forces_axial)

    def update_forces_tangent(self, actuator_force: ActuatorForceTangent) -> None:
        """Update the tangent actuator forces.

        Parameters
        ----------
        actuator_force : `ActuatorForceTangent`
            Tangent actuator force.

        Raises
        ------
        `ValueError`
            When the input is the same object of self.forces_tangent.
        """

        if id(actuator_force) == id(self.forces_tangent):
            raise ValueError("Input cannot be the same object of self.forces_tangent.")

        self.forces_tangent = actuator_force
        self.signal_detailed_force.forces_tangent.emit(self.forces_tangent)

    def update_force_error_tangent(
        self, force_error_tangent: ForceErrorTangent
    ) -> None:
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

    def update_position(
        self,
        x: float,
        y: float,
        z: float,
        rx: float,
        ry: float,
        rz: float,
        is_ims: bool = False,
    ) -> None:
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
        is_ims : `bool`, optional
            Is based on the independent measurement system (IMS) or not. (the
            default is False)
        """

        # Decide the position and signal objects
        position = self.position_ims if is_ims else self.position
        signal = (
            self.signal_position.position_ims
            if is_ims
            else self.signal_position.position
        )

        tol = get_tol(self.NUM_DIGIT_AFTER_DECIMAL)

        is_changed = False
        components = [x, y, z, rx, ry, rz]
        for idx, component in enumerate(components):
            if self._has_changed(position[idx], component, tol):
                is_changed = True
                break

        if is_changed:
            for idx, component in enumerate(components):
                position[idx] = round(component, self.NUM_DIGIT_AFTER_DECIMAL)

            signal.emit(position)

    def update_net_force_moment_total(
        self,
        value_new: list[float],
        is_force: bool = True,
    ) -> None:
        """Update the total net force or moment.

        Parameters
        ----------
        value_new : `list`
            New (x, y, z) component values. Unit is Newton or Newton * meter
            based on 'is_force'.
        is_force : `bool`, optional
            Is the force data or not. If not, the moment data is applied. (the
            default is True)
        """

        # Decide the value to compare and the related signal
        value_old = self.net_force_total if is_force else self.net_moment_total

        signal = (
            self.signal_net_force_moment.net_force_total
            if is_force
            else self.signal_net_force_moment.net_moment_total
        )

        tol = get_tol(self.NUM_DIGIT_AFTER_DECIMAL)
        if self._has_changed(np.array(value_old), np.array(value_new), tol):
            for idx, value in enumerate(value_new):
                value_old[idx] = round(value, self.NUM_DIGIT_AFTER_DECIMAL)

            signal.emit(value_old)

    def update_force_balance(self, value_new: list[float]) -> None:
        """Update the force balance status.

        Parameters
        ----------
        value_new : `list`
            New (fx, fy, fz, mx, my, mz) component values. Unit is Newton or
            Newton * meter that depends on the component is force or moment.
        """

        tol = get_tol(self.NUM_DIGIT_AFTER_DECIMAL)
        if self._has_changed(np.array(self.force_balance), np.array(value_new), tol):
            for idx, value in enumerate(value_new):
                self.force_balance[idx] = round(value, self.NUM_DIGIT_AFTER_DECIMAL)

            self.signal_net_force_moment.force_balance.emit(self.force_balance)
