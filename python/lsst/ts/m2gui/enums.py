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
    "LocalMode",
    "LimitSwitchType",
    "Ring",
    "PowerType",
    "TemperatureGroup",
    "DisplacementSensorDirection",
]

from enum import IntEnum, auto


class LocalMode(IntEnum):
    Standby = 1
    Diagnostic = auto()
    Enable = auto()


class LimitSwitchType(IntEnum):
    Retract = 1
    Extend = auto()


class Ring(IntEnum):
    A = 1
    B = auto()
    C = auto()
    D = auto()


class PowerType(IntEnum):
    Motor = 1
    Communication = auto()


class TemperatureGroup(IntEnum):
    Intake = 1
    Exhaust = auto()
    LG2 = auto()
    LG3 = auto()
    LG4 = auto()


class DisplacementSensorDirection(IntEnum):
    Theta = 1
    Delta = auto()
