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

__all__ = ["SignalLimitSwitch"]

from PySide2 import QtCore


class SignalLimitSwitch(QtCore.QObject):
    """Status signal to send the event of limit switch status."""

    # The type_name_status should be a tuple: (type, name, status). The data
    # type of "type" is integer (enum "LimitSwitchType"), the data type of
    # "name" is string, and the data type of "status" is bool. If the limit
    # switch is triggered, put the "status" as True, otherwise, False.
    type_name_status = QtCore.Signal(object)
