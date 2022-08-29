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

import logging

import pytest
from lsst.ts.m2gui import FaultManager, LimitSwitchType, Model, Ring

TIMEOUT = 1000


@pytest.fixture
def fault_manager():

    model = Model(logging.getLogger())
    fault_manager = FaultManager(model.get_actuator_default_status(False))

    return fault_manager


def test_init(fault_manager):

    assert len(fault_manager.limit_switch_status_retract) == 78
    assert len(fault_manager.limit_switch_status_extend) == 78


def test_add_error(qtbot, fault_manager):

    error = 3

    with qtbot.waitSignal(fault_manager.signal_error.error_new, timeout=TIMEOUT):
        fault_manager.add_error(error)

    assert fault_manager.errors == {error}


def test_add_error_repeat(qtbot, fault_manager):

    error = 3
    fault_manager.add_error(error)

    with qtbot.assertNotEmitted(fault_manager.signal_error.error_new, wait=TIMEOUT):
        fault_manager.add_error(error)

    assert fault_manager.errors == {error}


def test_clear_error(qtbot, fault_manager):

    error = 3
    fault_manager.add_error(error)

    with qtbot.waitSignal(fault_manager.signal_error.error_cleared, timeout=TIMEOUT):
        fault_manager.clear_error(error)

    assert fault_manager.errors == set()


def test_clear_error_not_existed(qtbot, fault_manager):

    with qtbot.assertNotEmitted(fault_manager.signal_error.error_cleared, wait=TIMEOUT):
        fault_manager.clear_error(3)

    assert fault_manager.errors == set()


def test_reset_errors(qtbot, fault_manager):

    fault_manager.add_error(1)
    fault_manager.add_error(2)

    with qtbot.waitSignal(fault_manager.signal_error.error_cleared, timeout=TIMEOUT):
        fault_manager.reset_errors()

    assert fault_manager.errors == set()


def test_reset_errors_no_error(qtbot, fault_manager):

    with qtbot.assertNotEmitted(fault_manager.signal_error.error_cleared, wait=TIMEOUT):
        fault_manager.reset_errors()

    assert fault_manager.errors == set()


def test_has_error(fault_manager):

    assert fault_manager.has_error() is False

    fault_manager.add_error(1)

    assert fault_manager.has_error() is True


def test_reset_limit_switch_status_retract(qtbot, fault_manager):

    fault_manager.update_limit_switch_status(LimitSwitchType.Retract, Ring.B, 2, True)

    with qtbot.waitSignal(
        fault_manager.signal_limit_switch.type_name_status, timeout=TIMEOUT
    ):
        fault_manager.reset_limit_switch_status(LimitSwitchType.Retract)

    assert fault_manager.limit_switch_status_retract["B2"] is False


def test_reset_limit_switch_status_extend(qtbot, fault_manager):

    fault_manager.update_limit_switch_status(LimitSwitchType.Extend, Ring.C, 3, True)

    with qtbot.waitSignal(
        fault_manager.signal_limit_switch.type_name_status, timeout=TIMEOUT
    ):
        fault_manager.reset_limit_switch_status(LimitSwitchType.Extend)

    assert fault_manager.limit_switch_status_extend["C3"] is False


def test_update_limit_switch_status(qtbot, fault_manager):

    with qtbot.waitSignal(
        fault_manager.signal_limit_switch.type_name_status, timeout=TIMEOUT
    ):
        fault_manager.update_limit_switch_status(
            LimitSwitchType.Extend, Ring.C, 3, True
        )

    assert fault_manager.limit_switch_status_extend["C3"] is True


def test_update_limit_switch_status_exception(fault_manager):

    with pytest.raises(ValueError):
        fault_manager.update_limit_switch_status("wrong_type", Ring.B, 1, True)

    with pytest.raises(ValueError):
        fault_manager.update_limit_switch_status(
            LimitSwitchType.Retract, Ring.B, 100, True
        )
