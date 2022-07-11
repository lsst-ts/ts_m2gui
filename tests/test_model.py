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
import logging

from lsst.ts.m2gui import (
    Model,
    LocalMode,
    LimitSwitchType,
    Ring,
    CommandScript,
    CommandActuator,
)


TIMEOUT = 1000


@pytest.fixture
def model():
    return Model(logging.getLogger())


def test_init(model):

    assert len(model.system_status) == 9


def test_add_error(qtbot, model):

    error = 3
    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        model.add_error(error)

    assert model.fault_manager.errors == {error}


def test_clear_error(qtbot, model):

    error = 3
    model.add_error(error)

    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        model.clear_error(error)

    assert model.fault_manager.errors == set()


def test_reset_errors(qtbot, model):

    model.add_error(3)
    model.fault_manager.update_limit_switch_status(
        LimitSwitchType.Retract, Ring.B, 2, True
    )
    model.fault_manager.update_limit_switch_status(
        LimitSwitchType.Extend, Ring.C, 3, True
    )

    signals = [
        model.fault_manager.signal_error.error_cleared,
        model.fault_manager.signal_limit_switch.type_name_status,
        model.signal_status.name_status,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        model.reset_errors()

    assert model.fault_manager.errors == set()
    assert model.fault_manager.limit_switch_status_retract["B2"] is False
    assert model.fault_manager.limit_switch_status_extend["C3"] is False


def test_enable_open_loop_max_limit(model):

    # Should fail for the wrong local state
    with pytest.raises(RuntimeError):
        model.enable_open_loop_max_limit()

    assert model.system_status["isOpenLoopMaxLimitsEnabled"] is False

    # Should succeed for the correct state
    model.local_mode = LocalMode.Enable

    model.enable_open_loop_max_limit()

    assert model.system_status["isOpenLoopMaxLimitsEnabled"] is True


def test_disable_open_loop_max_limit(model):

    model.local_mode = LocalMode.Enable
    model.enable_open_loop_max_limit()

    model.disable_open_loop_max_limit()

    assert model.system_status["isOpenLoopMaxLimitsEnabled"] is False


def test_update_system_status(qtbot, model):

    status_name = "isTelemetryActive"

    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        model.update_system_status(status_name, True)

    assert model.system_status[status_name] is True


def test_update_system_status_exception(model):

    with pytest.raises(ValueError):
        model.update_system_status("wrong_name", True)


def test_report_config(qtbot, model):

    file_configuration = "test"

    with qtbot.waitSignal(model.signal_config.config, timeout=TIMEOUT):
        config = model.report_config(file_configuration=file_configuration)

    assert config.file_configuration == file_configuration


def test_report_script_progress(qtbot, model):

    with qtbot.waitSignal(model.signal_script.progress, timeout=TIMEOUT):
        model.report_script_progress(30)


def test_report_config_exception(model):

    with pytest.raises(KeyError):
        model.report_config(wrong_name=0)


def test_is_enabled_and_open_loop_control(model):

    assert model.is_enabled_and_open_loop_control() is False

    model.local_mode = LocalMode.Enable
    assert model.is_enabled_and_open_loop_control() is True

    model.is_closed_loop = True
    assert model.is_enabled_and_open_loop_control() is False


def test_is_enabled_and_closed_loop_control(model):

    assert model.is_enabled_and_closed_loop_control() is False

    model.local_mode = LocalMode.Enable
    assert model.is_enabled_and_closed_loop_control() is False

    model.is_closed_loop = True
    assert model.is_enabled_and_closed_loop_control() is True


def test_go_to_position_exception(model):

    with pytest.raises(RuntimeError):
        model.go_to_position(0, 0, 0, 0, 0, 0)


def test_reboot_controller_exception(model):

    with pytest.raises(RuntimeError):
        model.local_mode = LocalMode.Diagnostic
        model.reboot_controller()

    with pytest.raises(RuntimeError):
        model.is_csc_commander = True
        model.reboot_controller()


def test_set_bit_digital_status_exception(model):

    with pytest.raises(RuntimeError):
        model.set_bit_digital_status(0, 1)


def test_command_script_exception(model):

    with pytest.raises(RuntimeError):
        model.command_script(CommandScript.LoadScript)


def test_command_actuator_exception(model):

    with pytest.raises(RuntimeError):
        model.command_actuator(CommandActuator.Stop)

    model.local_mode = LocalMode.Enable
    with pytest.raises(RuntimeError):
        model.command_actuator(CommandActuator.Start, actuators=[])


def test_update_connection_information(model):

    model.update_connection_information("test", 1, 2, 3)

    assert model.host == "test"
    assert model.port_command == 1
    assert model.port_telemetry == 2
    assert model.timeout_connection == 3


def test_update_connection_information_exception(model):

    model.system_status["isCrioConnected"] = True
    with pytest.raises(RuntimeError):
        model.update_connection_information("test", 1, 2, 3)


def test_connect_exception(model):

    model.system_status["isCrioConnected"] = True
    with pytest.raises(RuntimeError):
        model.connect()


def test_disconnect_exception(model):

    with pytest.raises(RuntimeError):
        model.disconnect()
