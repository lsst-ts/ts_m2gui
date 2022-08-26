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

import asyncio

import pytest
from lsst.ts.m2gui import Ring, get_num_actuator_ring, get_tol, run_command


def command_normal(is_failed):

    if is_failed:
        raise RuntimeError("Command is failed.")


async def command_coroutine(is_failed):

    await asyncio.sleep(0.5)

    if is_failed:
        raise RuntimeError("Command is failed.")


def test_get_tol():

    assert get_tol(1) == 0.1
    assert get_tol(2) == 0.01


def test_get_num_actuator_ring():

    assert get_num_actuator_ring(Ring.A) == 6
    assert get_num_actuator_ring(Ring.B) == 30
    assert get_num_actuator_ring(Ring.C) == 24
    assert get_num_actuator_ring(Ring.D) == 18

    with pytest.raises(ValueError):
        get_num_actuator_ring("WrongRing")


async def test_run_command(qtbot):
    # Note that we need to add the "qtbot" here as the argument for the event
    # loop or GUI to run

    assert await run_command(command_normal, False) is True
    assert await run_command(command_normal, True, is_prompted=False) is False

    assert await run_command(command_coroutine, False) is True
    assert await run_command(command_coroutine, True, is_prompted=False) is False
