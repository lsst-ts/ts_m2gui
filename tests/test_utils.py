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

import pytest
import pathlib

from lsst.ts.m2gui import (
    get_tol,
    get_num_actuator_ring,
    Ring,
    run_command,
    read_yaml_file,
)


def command(is_failed):

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


def test_run_command(qtbot):
    # Note that we need to add the "qtbot" here as the argument for the event
    # loop or GUI to run

    assert run_command(command, False) is True
    assert run_command(command, True, is_prompted=False) is False


def test_read_yaml_file():

    yaml_file = pathlib.Path(__file__).parents[0] / ".." / "policy" / "default.yaml"

    content = read_yaml_file(yaml_file)

    assert content["host"] == "m2-crio-controller01.cp.lsst.org"
    assert content["port_command"] == 50010
    assert content["port_telemetry"] == 50011
    assert content["timeout_connection"] == 10


def test_read_yaml_file_exception():

    with pytest.raises(IOError):
        read_yaml_file("no_this_yaml_file.yaml")
