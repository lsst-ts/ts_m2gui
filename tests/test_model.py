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
import pytest_asyncio
from lsst.ts import salobj
from lsst.ts.m2com import NUM_ACTUATOR, NUM_TANGENT_LINK, CommandActuator, CommandScript
from lsst.ts.m2gui import LimitSwitchType, LocalMode, Model, Ring

TIMEOUT = 1000
TIMEOUT_LONG = 2000


@pytest.fixture
def model():
    return Model(logging.getLogger())


@pytest_asyncio.fixture
async def model_async():
    async with Model(logging.getLogger(), is_simulation_mode=True) as model_sim:
        await model_sim.connect()
        yield model_sim


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


@pytest.mark.asyncio
async def test_reset_errors(qtbot, model_async):

    assert model_async.controller.are_clients_connected() is True

    model_async.add_error(3)
    model_async.fault_manager.update_limit_switch_status(
        LimitSwitchType.Retract, Ring.B, 2, True
    )
    model_async.fault_manager.update_limit_switch_status(
        LimitSwitchType.Extend, Ring.C, 3, True
    )

    signals = [
        model_async.fault_manager.signal_error.error_cleared,
        model_async.fault_manager.signal_limit_switch.type_name_status,
        model_async.signal_status.name_status,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        await model_async.reset_errors()

    assert model_async.fault_manager.errors == set()
    assert model_async.fault_manager.limit_switch_status_retract["B2"] is False
    assert model_async.fault_manager.limit_switch_status_extend["C3"] is False


@pytest.mark.asyncio
async def test_enable_open_loop_max_limit(model_async):

    # Should fail for the closed-loop control
    model_async.is_closed_loop = True
    with pytest.raises(RuntimeError):
        await model_async.enable_open_loop_max_limit()

    assert model_async.system_status["isOpenLoopMaxLimitsEnabled"] is False

    # Should succeed for the open-loop control
    model_async.is_closed_loop = False

    await model_async.enable_open_loop_max_limit()

    assert model_async.system_status["isOpenLoopMaxLimitsEnabled"] is True


def test_disable_open_loop_max_limit(model):

    model.system_status["isOpenLoopMaxLimitsEnabled"] = True

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


@pytest.mark.asyncio
async def test_go_to_position_exception(model):

    with pytest.raises(RuntimeError):
        await model.go_to_position(0, 0, 0, 0, 0, 0)


@pytest.mark.asyncio
async def test_reboot_controller_exception(model):

    with pytest.raises(RuntimeError):
        model.local_mode = LocalMode.Diagnostic
        await model.reboot_controller()

    with pytest.raises(RuntimeError):
        model.is_csc_commander = True
        await model.reboot_controller()


def test_set_bit_digital_status_exception(model):

    with pytest.raises(RuntimeError):
        model.set_bit_digital_status(0, 1)


@pytest.mark.asyncio
async def test_command_script_exception(model):

    with pytest.raises(RuntimeError):
        await model.command_script(CommandScript.LoadScript)


@pytest.mark.asyncio
async def test_command_actuator_exception(model):

    with pytest.raises(RuntimeError):
        await model.command_actuator(CommandActuator.Stop)

    model.local_mode = LocalMode.Enable
    with pytest.raises(RuntimeError):
        await model.command_actuator(CommandActuator.Start, actuators=[])


@pytest.mark.asyncio
async def test_reset_breakers(qtbot, model_async):

    # Transition to the Enabled state to power on the motor and communication
    controller = model_async.controller
    await controller.write_command_to_server(
        "start", controller_state_expected=salobj.State.DISABLED
    )
    await controller.write_command_to_server(
        "enable", controller_state_expected=salobj.State.ENABLED
    )

    model_async.utility_monitor.update_breaker("J1-W9-1", True)

    with qtbot.waitSignal(
        model_async.utility_monitor.signal_utility.breaker_status, timeout=TIMEOUT_LONG
    ):
        await model_async.reset_breakers()


def test_update_connection_information(model):

    model.update_connection_information("test", 1, 2, 3)

    controller = model.controller
    assert controller.host == "test"
    assert controller.port_command == 1
    assert controller.port_telemetry == 2
    assert controller.timeout_connection == 3


def test_update_connection_information_exception(model):

    with pytest.raises(ValueError):
        model.update_connection_information("test", 1, 1, 3)

    model.system_status["isCrioConnected"] = True
    with pytest.raises(RuntimeError):
        model.update_connection_information("test", 1, 2, 3)


@pytest.mark.asyncio
async def test_connect_exception(model):

    model.system_status["isCrioConnected"] = True
    with pytest.raises(RuntimeError):
        await model.connect()


def test_process_event(qtbot, model):

    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        model._process_event({"id": "m2AssemblyInPosition", "inPosition": True})

    with qtbot.waitSignal(model.signal_control.is_control_updated, timeout=TIMEOUT):
        model._process_event(
            {"id": "summaryState", "summaryState": salobj.State.DISABLED}
        )
    assert model.local_mode == LocalMode.Diagnostic

    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        model._process_event({"id": "errorCode", "errorCode": 1})

    with qtbot.waitSignal(model.signal_control.is_control_updated, timeout=TIMEOUT):
        model._process_event({"id": "commandableByDDS", "state": True})
    assert model.is_csc_commander is True

    with qtbot.waitSignal(
        model.utility_monitor.signal_detailed_force.hard_points, timeout=TIMEOUT
    ):
        model._process_event({"id": "hardpointList", "actuators": [1, 2, 3, 4, 5, 6]})

    with qtbot.waitSignal(model.signal_control.is_control_updated, timeout=TIMEOUT):
        model._process_event({"id": "forceBalanceSystemStatus", "status": True})
    assert model.is_closed_loop is True

    with qtbot.waitSignal(model.signal_script.progress, timeout=TIMEOUT):
        model._process_event({"id": "scriptExecutionStatus", "percentage": 1})

    with qtbot.waitSignal(
        model.utility_monitor.signal_utility.digital_status_output, timeout=TIMEOUT
    ):
        model._process_event({"id": "digitalOutput", "value": 1})

    with qtbot.waitSignal(
        model.utility_monitor.signal_utility.digital_status_input, timeout=TIMEOUT
    ):
        model._process_event({"id": "digitalInput", "value": 1})


def test_get_message_name(model):

    assert model._get_message_name("") == ""
    assert model._get_message_name(dict()) == ""

    assert model._get_message_name({"id": "test"}) == "test"


def test_summary_state_to_local_mode(model):

    assert model._summary_state_to_local_mode(salobj.State.STANDBY) == LocalMode.Standby
    assert (
        model._summary_state_to_local_mode(salobj.State.DISABLED)
        == LocalMode.Diagnostic
    )
    assert model._summary_state_to_local_mode(salobj.State.ENABLED) == LocalMode.Enable

    # Check the Fault state
    assert model._summary_state_to_local_mode(salobj.State.FAULT) == LocalMode.Standby

    model.local_mode = LocalMode.Enable
    assert (
        model._summary_state_to_local_mode(salobj.State.FAULT) == LocalMode.Diagnostic
    )


def test_process_telemetry(qtbot, model):

    with qtbot.waitSignal(
        model.utility_monitor.signal_position.position, timeout=TIMEOUT
    ):
        model._process_telemetry(
            {"id": "position", "x": 1, "y": 1, "z": 1, "xRot": 1, "yRot": 1, "zRot": 1}
        )

    num_axial = NUM_ACTUATOR - NUM_TANGENT_LINK
    with qtbot.waitSignal(
        model.utility_monitor.signal_detailed_force.forces, timeout=TIMEOUT
    ):
        model._process_telemetry(
            {
                "id": "axialForce",
                "lutGravity": [1] * num_axial,
                "lutTemperature": [1] * num_axial,
                "applied": [1] * num_axial,
                "measured": [1] * num_axial,
                "hardpointCorrection": [1] * num_axial,
            }
        )

    with qtbot.waitSignal(
        model.utility_monitor.signal_detailed_force.forces, timeout=TIMEOUT
    ):
        model._process_telemetry(
            {
                "id": "tangentForce",
                "lutGravity": [1] * NUM_TANGENT_LINK,
                "applied": [1] * NUM_TANGENT_LINK,
                "measured": [1] * NUM_TANGENT_LINK,
                "hardpointCorrection": [1] * NUM_TANGENT_LINK,
            }
        )

    with qtbot.waitSignal(
        model.utility_monitor.signal_utility.temperatures, timeout=TIMEOUT
    ):
        model._process_telemetry(
            {
                "id": "temperature",
                "intake": [1] * 2,
                "exhaust": [1] * 2,
                "ring": [1] * 12,
            }
        )

    with qtbot.waitSignal(
        model.utility_monitor.signal_utility.inclinometer, timeout=TIMEOUT
    ):
        model._process_telemetry(
            {
                "id": "zenithAngle",
                "inclinometerProcessed": 1,
            }
        )

    with qtbot.waitSignal(
        model.utility_monitor.signal_detailed_force.forces, timeout=TIMEOUT
    ):
        model._process_telemetry(
            {
                "id": "axialEncoderPositions",
                "position": [10000] * num_axial,
            }
        )

    with qtbot.waitSignal(
        model.utility_monitor.signal_detailed_force.forces, timeout=TIMEOUT
    ):
        model._process_telemetry(
            {
                "id": "tangentEncoderPositions",
                "position": [10000] * NUM_TANGENT_LINK,
            }
        )

    with qtbot.waitSignal(
        model.utility_monitor.signal_utility.displacements, timeout=TIMEOUT
    ):
        num_sensor = 6
        model._process_telemetry(
            {
                "id": "displacementSensors",
                "thetaZ": [1] * num_sensor,
                "deltaZ": [1] * num_sensor,
            }
        )

    with qtbot.waitSignals(
        [
            model.utility_monitor.signal_utility.power_motor_calibrated,
            model.utility_monitor.signal_utility.power_communication_calibrated,
        ],
        timeout=TIMEOUT,
    ):
        num_sensor = 6
        model._process_telemetry(
            {
                "id": "powerStatus",
                "motorVoltage": 1,
                "motorCurrent": 1,
                "commVoltage": 1,
                "commCurrent": 1,
            }
        )
