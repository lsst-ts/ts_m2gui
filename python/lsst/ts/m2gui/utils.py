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
    "get_num_actuator_ring",
    "map_actuator_id_to_alias",
    "read_ilc_status_from_log",
    "sum_ilc_lost_comm",
]

import ast
import re
from pathlib import Path

import numpy as np
from lsst.ts.m2com import NUM_ACTUATOR

from .enums import Ring


def get_num_actuator_ring(ring: Ring) -> int:
    """Get the number of actuators on the specific ring.

    Parameters
    ----------
    ring : enum `Ring`
        Specific ring.

    Returns
    -------
    `int`
        Number of the actuators.

    Raises
    ------
    `ValueError`
        Not supported ring.
    """

    if ring == Ring.A:
        return 6
    elif ring == Ring.B:
        return 30
    elif ring == Ring.C:
        return 24
    elif ring == Ring.D:
        return 18
    else:
        raise ValueError(f"Not supported ring: {ring!r}")


def map_actuator_id_to_alias(actuator_id: int) -> tuple[Ring, int]:
    """Map the actuator ID to the alias.

    Parameters
    ----------
    actuator_id : `int`
        Actuator ID that begins from 0.

    Returns
    -------
    ring : enum `Ring`
        Ring.
    actuator_id_plus_one : `int`
        Number of the actuator on the ring.

    Raises
    ------
    `ValueError`
        Unknown actuator ID encountered.
    """

    # Alias begins from 1 instead of 0
    actuator_id_plus_one = actuator_id + 1

    # Look for the alias
    ring_order = (Ring.B, Ring.C, Ring.D, Ring.A)
    for ring in ring_order:
        num_actuators = get_num_actuator_ring(ring)

        if actuator_id_plus_one <= num_actuators:
            return ring, actuator_id_plus_one
        else:
            actuator_id_plus_one -= num_actuators

    raise ValueError(f"Unknown actuator ID ({actuator_id}) encountered.")


def read_ilc_status_from_log(
    filepath: Path | str, keyword: str = "ILC status"
) -> list[list[int]]:
    """Read the inner-loop controller (ILC) status from the log file.

    Parameters
    ----------
    filepath : `Path` or `str`
        Log file path.
    keyword : `str`, optional
        Keyword in the log file. (the default is "ILC status")

    Returns
    -------
    ilc_status : `list`
        ILC status.
    """

    ilc_status = list()
    with open(filepath, "r") as file:
        for line in file:
            if keyword in line:
                result = re.match(r".+(\[.+\])", line)

                if result is not None:
                    ilc_status.append(ast.literal_eval(result.group(1)))

    return ilc_status


def sum_ilc_lost_comm(ilc_status: list[list[int]]) -> list[int]:
    """Summarize the lost communication of inner-loop controller (ILC).

    Parameters
    ----------
    ilc_status : `list`
        ILC status.

    Returns
    -------
    `list`
        Summarized lost communication.
    """

    ilc_lost_communication = np.zeros(NUM_ACTUATOR, dtype=int)

    ilc_data = np.array(ilc_status)
    for data in ilc_data:
        lost_value = (data == 0).astype(int)
        if np.sum(lost_value) != NUM_ACTUATOR:
            ilc_lost_communication = ilc_lost_communication + lost_value

    return ilc_lost_communication.tolist()
