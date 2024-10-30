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

import tempfile
from pathlib import Path

import pytest
from lsst.ts.m2com import NUM_ACTUATOR
from lsst.ts.m2gui import (
    Ring,
    get_num_actuator_ring,
    map_actuator_id_to_alias,
    read_ilc_status_from_log,
    sum_ilc_lost_comm,
)


def test_get_num_actuator_ring() -> None:
    assert get_num_actuator_ring(Ring.A) == 6
    assert get_num_actuator_ring(Ring.B) == 30
    assert get_num_actuator_ring(Ring.C) == 24
    assert get_num_actuator_ring(Ring.D) == 18

    with pytest.raises(ValueError):
        get_num_actuator_ring("WrongRing")


def test_map_actuator_id_to_alias() -> None:
    ring_b, num_b = map_actuator_id_to_alias(3)
    assert ring_b == Ring.B
    assert num_b == 4

    ring_a, num_a = map_actuator_id_to_alias(72)
    assert ring_a == Ring.A
    assert num_a == 1

    with pytest.raises(ValueError):
        map_actuator_id_to_alias(78)


def test_read_ilc_status_from_log() -> None:
    ilc_status_message = [16] * NUM_ACTUATOR
    log_message = (
        f"This is a test log file.\n"
        f"2023-07-18, DEBUG, Receive ILC status: {ilc_status_message}.\n"
        f"2023-07-19, DEBUG, Receive ILC status: {ilc_status_message}."
    )

    file = tempfile.NamedTemporaryFile()
    file.seek(0)
    file.write(log_message.encode())
    file.flush()

    filepath = Path(file.name)
    ilc_status = read_ilc_status_from_log(filepath)

    assert ilc_status == [ilc_status_message, ilc_status_message]


def test_sum_ilc_lost_comm() -> None:
    # Prepare the ILC status
    ilc_status_1 = [0] * NUM_ACTUATOR
    ilc_status_2 = [0] + [1] * (NUM_ACTUATOR - 1)
    ilc_status_3 = [0, 0] + [1] * (NUM_ACTUATOR - 2)

    ilc_status = [ilc_status_1, ilc_status_2, ilc_status_3]

    # Summarize the lost communication
    lost_comm = sum_ilc_lost_comm(ilc_status)

    assert lost_comm == [2, 1] + [0] * (NUM_ACTUATOR - 2)
