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

__all__ = ["Config"]

from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class to have the configuration details."""

    file_configuration: str = ""
    file_version: str = ""
    file_control_parameters: str = ""
    file_lut_parameters: str = ""

    # In percent
    power_warning_motor: float = 0
    # In percent
    power_fault_motor: float = 0
    # In amps
    power_threshold_motor: float = 0

    # In percent
    power_warning_communication: float = 0
    # In percent
    power_fault_communication: float = 0
    # In amps
    power_threshold_communication: float = 0

    # In newton
    in_position_axial: float = 0
    # In newton
    in_position_tangent: float = 0
    # In second
    in_position_sample: float = 0

    # In second
    timeout_sal: float = 0
    # In second
    timeout_crio: float = 0
    # In count
    timeout_ilc: int = 0

    # In degree
    misc_range_angle: float = 0
    misc_diff_enabled: bool = False

    # In degree C
    misc_range_temperature: float = 0
