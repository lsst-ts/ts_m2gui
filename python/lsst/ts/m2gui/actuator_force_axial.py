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

__all__ = ["ActuatorForceAxial"]

from dataclasses import dataclass, field
from typing import List

from lsst.ts.m2com import NUM_ACTUATOR, NUM_TANGENT_LINK

num_axial = NUM_ACTUATOR - NUM_TANGENT_LINK


@dataclass
class ActuatorForceAxial:
    """Axial actuator force class to have the force details contain the look-up
    table (LUT) information."""

    # The unit of force is Newton.

    # Force component in the calculation of gravity LUT.
    f_gravity: List[float] = field(default_factory=lambda: [0.0] * num_axial)
    f_delta: List[float] = field(default_factory=lambda: [0.0] * num_axial)

    # Force component in the calculation of temperature LUT.
    f_temperature: List[float] = field(default_factory=lambda: [0.0] * num_axial)

    # Current force
    f_cur: List[float] = field(default_factory=lambda: [0.0] * num_axial)

    # Force of the hard point correction
    f_hc: List[float] = field(default_factory=lambda: [0.0] * num_axial)

    # Force error
    f_error: List[float] = field(default_factory=lambda: [0.0] * num_axial)

    # Step of motor. The data type should be integer.
    step: List[int] = field(default_factory=lambda: [0] * num_axial)

    # Actuator position in millimeter
    position_in_mm: List[float] = field(default_factory=lambda: [0.0] * num_axial)
