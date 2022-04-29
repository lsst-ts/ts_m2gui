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

__all__ = [
    "SignalControl",
    "SignalError",
    "SignalLimitSwitch",
    "SignalMessage",
    "SignalStatus",
    "SignalConfig",
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
    """Configuration Signal to send the configuration."""

    config = QtCore.Signal(object)
