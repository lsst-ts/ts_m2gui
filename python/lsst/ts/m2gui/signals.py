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

__all__ = [
    "SignalControl",
    "SignalError",
    "SignalLimitSwitch",
    "SignalMessage",
    "SignalStatus",
    "SignalConfig",
    "SignalUtility",
    "SignalDetailedForce",
    "SignalPosition",
    "SignalScript",
]

from PySide2 import QtCore


class SignalControl(QtCore.QObject):
    """Control signal to send the event that the control is updated or
    not."""

    is_control_updated = QtCore.Signal(bool)


class SignalError(QtCore.QObject):
    """Error signal to send the error code."""

    # New error codes
    error_new = QtCore.Signal(int)

    # Cleared error codes
    error_cleared = QtCore.Signal(int)


class SignalLimitSwitch(QtCore.QObject):
    """Status signal to send the event of limit switch status."""

    # The type_name_status should be a tuple: (type, name, status). The data
    # type of "type" is integer (enum "LimitSwitchType"), the data type of
    # "name" is string, and the data type of "status" is bool. If the limit
    # switch is triggered, put the "status" as True, otherwise, False.
    type_name_status = QtCore.Signal(object)


class SignalMessage(QtCore.QObject):
    """Message signal to send the message event."""

    message = QtCore.Signal(str)


class SignalStatus(QtCore.QObject):
    """Status signal to send the event of system status."""

    # The name_status should be a tuple: (name, status). The data type of name
    # is string and the data type of status is bool.
    name_status = QtCore.Signal(object)


class SignalConfig(QtCore.QObject):
    """Configuration signal to send the configuration."""

    # Instance of `Config` class.
    config = QtCore.Signal(object)


class SignalUtility(QtCore.QObject):
    """Utility signal to send the utility status."""

    # Calibrated power data
    # The power should be a tuple: (voltage, current). The data type is float.
    # The units are volt and ampere respectively.
    power_motor_calibrated = QtCore.Signal(object)
    power_communication_calibrated = QtCore.Signal(object)

    # Raw power data (debug only)
    # The power should be a tuple: (voltage, current). The data type is float.
    # The units are volt and ampere respectively.
    power_motor_raw = QtCore.Signal(object)
    power_communication_raw = QtCore.Signal(object)

    # M2 inclinometer angle in degree
    inclinometer = QtCore.Signal(float)

    # Telescope mount assembly (TMA) inclinometer angle in degree
    inclinometer_tma = QtCore.Signal(float)

    # The breaker_status should be a tuple: (name, status). The data type of
    # "name" is string, and the data type of "status" is bool. If the breaker
    # is triggered, put the "status" as True, otherwise, False.
    breaker_status = QtCore.Signal(object)

    # The temperatures should be a tuple:
    # (temperature_group, [temperture_1, temperture_2, ...]). The data type of
    # "temperature_group" is the enum: `TemperatureGroup`. The data type of the
    # temperature in "[temperture_1, temperture_2, ...]" is float. The unit is
    # degree C. This list should have all the temperatures in the group.
    temperatures = QtCore.Signal(object)

    # The displacements should be a tuple:
    # (sensor_direction, [displacement_1, displacement_2, ...]). The data type
    # of "sensor_direction" is the enum: `DisplacementSensorDirection`. The
    # data type of displacement in "[displacement_1, displacement_2, ...]" is
    # float. The unit is mm. This list should have all the displacements in the
    # direction.
    displacements = QtCore.Signal(object)

    # Digital input/output status as 32/8 bits value. Each bit means different
    # status. 1 means OK (or triggered). Otherwise 0.
    # Note the input data type needs to be object instead of int, which is 4
    # bytes by default in QT. Otherwise, it will result in the overflow error.
    digital_status_input = QtCore.Signal(object)
    digital_status_output = QtCore.Signal(int)


class SignalDetailedForce(QtCore.QObject):
    """Detailed force signal to send the calculated and measured force details
    contains the look-up table (LUT)."""

    # List of the hard points. There should be 6 elements. The first three are
    # the axial actuators and the last three are the tangential actuators.
    hard_points = QtCore.Signal(object)

    # Instance of the `ActuatorForce` class.
    forces = QtCore.Signal(object)

    # Tangential force error to monitor the supporting force of tangential
    # link. Instance of `ForceErrorTangent` class.
    force_error_tangent = QtCore.Signal(object)


class SignalPosition(QtCore.QObject):
    """Position signal to send the rigid body position."""

    # Rigid body position as a list: [x, y, z, rx, ry, rz]. The unit of x, y,
    # and z is um. The unit of rx, ry, and ry is arcsec.
    position = QtCore.Signal(object)


class SignalScript(QtCore.QObject):
    """Script signal to send the status of script progress."""

    # Progress of the script execution.
    progress = QtCore.Signal(int)
