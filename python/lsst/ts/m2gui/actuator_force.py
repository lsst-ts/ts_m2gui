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

__all__ = ["ActuatorForce"]

from dataclasses import dataclass, field

from . import NUM_ACTUATOR


@dataclass
class ActuatorForce:
    """Actuator force class to have the force details contain the look-up table
    (LUT) information."""

    # The unit of force is Newton.

    # Force component in the calculation of gravity LUT.
    f_e: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)
    f_0: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)
    f_a: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)
    f_f: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)
    f_delta: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)

    # Force component in the calculation of temperature LUT.
    t_u: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)
    t_x: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)
    t_y: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)
    t_r: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)

    # Commanded force
    f_cmd: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)

    # Current force
    f_cur: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)

    # Force of the hard point correction
    f_hc: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)

    # Force error
    f_error: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)

    # Count of the encoder. The data type should be integer.
    encoder_count: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)

    # Step of motor. The data type should be integer.
    step: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)

    # Actuator position in millimeter
    position_in_mm: list = field(default_factory=lambda: [0] * NUM_ACTUATOR)
