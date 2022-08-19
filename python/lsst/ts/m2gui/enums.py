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
    "TemperatureGroup",
    "DisplacementSensorDirection",
]

from enum import IntEnum, auto


class LocalMode(IntEnum):
    """Operation mode of the engineering user interface (EUI)."""

    Standby = 1
    Diagnostic = auto()
    Enable = auto()


class LimitSwitchType(IntEnum):
    """Type of the limit switches on actuators."""

    Retract = 1
    Extend = auto()


class Ring(IntEnum):
    """Ring of the actuators. Each ring contains the different actuators. From
    the outer ring to the center, the order is A, B, C, and D ring. The A ring
    has the tangent links and the others have the axial actuators."""

    A = 1
    B = auto()
    C = auto()
    D = auto()


class TemperatureGroup(IntEnum):
    """Group of the temperature sensors."""

    Intake = 1
    Exhaust = auto()
    LG2 = auto()
    LG3 = auto()
    LG4 = auto()


class DisplacementSensorDirection(IntEnum):
    """Direction of the displacement sensors."""

    Theta = 1
    Delta = auto()


class FigureActuatorData(IntEnum):
    """Select the actuator data to show on the figures."""

    ForceMeasured = 1
    ForceError = auto()
    Displacement = auto()
