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

__all__ = ["ForceErrorTangent"]

from dataclasses import dataclass, field
from typing import List

from lsst.ts.m2com import NUM_TANGENT_LINK


@dataclass
class ForceErrorTangent:
    """Tangential link force error class to monitor the supporting force of
    mirror."""

    # The unit of force is Newton.

    error_force: List[int] = field(default_factory=lambda: [0] * NUM_TANGENT_LINK)
    error_weight: float = 0
    error_sum: float = 0
