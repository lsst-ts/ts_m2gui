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

import asyncio
import logging

import pytest
import pytest_asyncio
from lsst.ts.idl.enums import MTM2
from lsst.ts.m2com import (
    LIMIT_FORCE_AXIAL_CLOSED_LOOP,
    LIMIT_FORCE_AXIAL_OPEN_LOOP,
    LIMIT_FORCE_TANGENT_CLOSED_LOOP,
    LIMIT_FORCE_TANGENT_OPEN_LOOP,
    MAX_LIMIT_FORCE_AXIAL_OPEN_LOOP,
    MAX_LIMIT_FORCE_TANGENT_OPEN_LOOP,
    NUM_ACTUATOR,
    NUM_TANGENT_LINK,
    NUM_TEMPERATURE_EXHAUST,
    NUM_TEMPERATURE_INTAKE,
    NUM_TEMPERATURE_RING,
    CommandActuator,
    CommandScript,
    LimitSwitchType,
    PowerType,
)
from lsst.ts.m2gui import LocalMode, Model, Ring, Status
from pytestqt.qtbot import QtBot

TIMEOUT = 1000
TIMEOUT_LONG = 2000


@pytest.fixture
def model() -> Model:
    return Model(logging.getLogger())


@pytest_asyncio.fixture
async def model_async() -> Model:
    async with Model(logging.getLogger(), is_simulation_mode=True) as model_sim:
        await model_sim.connect()

        assert model_sim.fault_manager.has_error() is False

        yield model_sim


def test_init(model: Model) -> None:
    assert len(model.system_status) == 10


def test_report_error(qtbot: QtBot, model: Model) -> None:
    error = 3
    model.controller.error_handler.add_new_error(error)
    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        model.report_error(error)

    assert model.fault_manager.errors == {error}


def test_clear_error(qtbot: QtBot, model: Model) -> None:
    error = 3
    model.report_error(error)

    with qtbot.waitSignal(
        model.fault_manager.signal_error.error_cleared, timeout=TIMEOUT
    ):
        model.clear_error(error)

    assert model.fault_manager.errors == set()


@pytest.mark.asyncio
async def test_reset_errors(qtbot: QtBot, model_async: Model) -> None:
    assert model_async.controller.are_clients_connected() is True

    model_async.controller.error_handler.add_new_error(3)
    model_async.report_error(3)
    model_async.fault_manager.update_limit_switch_status(
        LimitSwitchType.Retract, Ring.B, 2, Status.Error
    )
    model_async.fault_manager.update_limit_switch_status(
        LimitSwitchType.Extend, Ring.C, 3, Status.Error
    )

    signals = [
        model_async.fault_manager.signal_error.error_cleared,
        model_async.fault_manager.signal_limit_switch.type_name_status,
        model_async.signal_status.name_status,
    ]
    with qtbot.waitSignals(signals, timeout=TIMEOUT):
        await model_async.reset_errors()

    assert model_async.fault_manager.errors == set()
    assert model_async.fault_manager.limit_switch_status_retract["B2"] == Status.Normal
    assert model_async.fault_manager.limit_switch_status_extend["C3"] == Status.Normal


@pytest.mark.asyncio
async def test_enable_open_loop_max_limit(model_async: Model) -> None:
    # Should fail for the closed-loop control
    model_async.is_closed_loop = True
    with pytest.raises(RuntimeError):
        await model_async.enable_open_loop_max_limit(True)

    assert model_async.system_status["isOpenLoopMaxLimitsEnabled"] is False

    # Should succeed for the open-loop control
    model_async.is_closed_loop = False

    await model_async.enable_open_loop_max_limit(True)

    await asyncio.sleep(1)

    assert model_async.system_status["isOpenLoopMaxLimitsEnabled"] is True


def test_update_system_status(qtbot: QtBot, model: Model) -> None:
    status_name = "isTelemetryActive"

    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        model.update_system_status(status_name, True)

    assert model.system_status[status_name] is True


def test_update_system_status_exception(model: Model) -> None:
    with pytest.raises(ValueError):
        model.update_system_status("wrong_name", True)


def test_report_config(qtbot: QtBot, model: Model) -> None:
    file_configuration = "test"

    with qtbot.waitSignal(model.signal_config.config, timeout=TIMEOUT):
        config = model.report_config(file_configuration=file_configuration)

    assert config.file_configuration == file_configuration


def test_report_script_progress(qtbot: QtBot, model: Model) -> None:
    with qtbot.waitSignal(model.signal_script.progress, timeout=TIMEOUT):
        model.report_script_progress(30)


def test_report_config_exception(model: Model) -> None:
    with pytest.raises(KeyError):
        model.report_config(wrong_name=0)


def test_is_enabled_and_open_loop_control(model: Model) -> None:
    assert model.is_enabled_and_open_loop_control() is False

    model.local_mode = LocalMode.Enable
    assert model.is_enabled_and_open_loop_control() is True

    model.is_closed_loop = True
    assert model.is_enabled_and_open_loop_control() is False


def test_is_enabled_and_closed_loop_control(model: Model) -> None:
    assert model.is_enabled_and_closed_loop_control() is False

    model.local_mode = LocalMode.Enable
    assert model.is_enabled_and_closed_loop_control() is False

    model.is_closed_loop = True
    assert model.is_enabled_and_closed_loop_control() is True


@pytest.mark.asyncio
async def test_go_to_position_exception(model: Model) -> None:
    with pytest.raises(RuntimeError):
        await model.go_to_position(0, 0, 0, 0, 0, 0)


@pytest.mark.asyncio
async def test_reboot_controller_exception(model: Model) -> None:
    with pytest.raises(RuntimeError):
        model.local_mode = LocalMode.Diagnostic
        await model.reboot_controller()

    with pytest.raises(RuntimeError):
        model.is_csc_commander = True
        await model.reboot_controller()


@pytest.mark.asyncio
async def test_command_script_exception(model: Model) -> None:
    with pytest.raises(RuntimeError):
        await model.command_script(CommandScript.LoadScript)


@pytest.mark.asyncio
async def test_command_actuator_exception(model: Model) -> None:
    with pytest.raises(RuntimeError):
        await model.command_actuator(CommandActuator.Stop)

    model.local_mode = LocalMode.Enable
    with pytest.raises(RuntimeError):
        await model.command_actuator(CommandActuator.Start, actuators=[])


@pytest.mark.asyncio
async def test_apply_actuator_force_exception(model: Model) -> None:
    with pytest.raises(RuntimeError):
        await model.apply_actuator_force([], 0.0)

    model.local_mode = LocalMode.Enable
    with pytest.raises(RuntimeError):
        await model.apply_actuator_force([1], 0.0)


@pytest.mark.asyncio
async def test_apply_actuator_force(model_async: Model) -> None:
    model_async.local_mode = LocalMode.Enable
    model_async.is_closed_loop = True
    force = 10.0
    await model_async.apply_actuator_force([1, 77], force)

    control_closed_loop = model_async.controller.mock_server.model.control_closed_loop
    assert control_closed_loop.axial_forces["applied"][1] == force
    assert control_closed_loop.tangent_forces["applied"][-1] == force


@pytest.mark.asyncio
async def test_reset_breakers(qtbot: QtBot, model_async: Model) -> None:
    # Power on the motor and communication first
    controller = model_async.controller
    await controller.power(PowerType.Communication, True)
    await controller.power(PowerType.Motor, True)

    model_async.utility_monitor.update_breaker("J1-W9-1", True)

    with qtbot.waitSignal(
        model_async.utility_monitor.signal_utility.breaker_status, timeout=TIMEOUT_LONG
    ):
        await model_async.reset_breakers(PowerType.Motor)


def test_update_connection_information(model: Model) -> None:
    model.update_connection_information("test", 1, 2, 3)

    controller = model.controller
    assert controller.host == "test"
    assert controller.port_command == 1
    assert controller.port_telemetry == 2
    assert controller.timeout_connection == 3


def test_update_connection_information_exception(model: Model) -> None:
    with pytest.raises(ValueError):
        model.update_connection_information("test", 1, 1, 3)

    model.system_status["isCrioConnected"] = True
    with pytest.raises(RuntimeError):
        model.update_connection_information("test", 1, 2, 3)


@pytest.mark.asyncio
async def test_connect_exception(model: Model) -> None:
    model.system_status["isCrioConnected"] = True
    with pytest.raises(RuntimeError):
        await model.connect()


@pytest.mark.asyncio
async def test_process_event(qtbot: QtBot, model: Model) -> None:
    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        await model._process_event(
            message={"id": "m2AssemblyInPosition", "inPosition": True}
        )

    with qtbot.waitSignal(model.fault_manager.signal_error.error_new, timeout=TIMEOUT):
        await model._process_event(message={"id": "errorCode", "errorCode": 1})

    with qtbot.waitSignal(model.signal_control.is_control_updated, timeout=TIMEOUT):
        await model._process_event(message={"id": "commandableByDDS", "state": True})
    assert model.is_csc_commander is True

    with qtbot.waitSignal(
        model.utility_monitor.signal_detailed_force.hard_points, timeout=TIMEOUT
    ):
        await model._process_event(
            message={"id": "hardpointList", "actuators": [1, 2, 3, 4, 5, 6]}
        )

    with qtbot.waitSignal(model.signal_control.is_control_updated, timeout=TIMEOUT):
        await model._process_event(
            message={"id": "forceBalanceSystemStatus", "status": True}
        )
    assert model.is_closed_loop is True

    with qtbot.waitSignal(model.signal_script.progress, timeout=TIMEOUT):
        await model._process_event(
            message={"id": "scriptExecutionStatus", "percentage": 1}
        )

    with qtbot.waitSignals(
        [
            model.utility_monitor.signal_utility.digital_status_output,
            model.signal_status.name_status,
        ],
        timeout=TIMEOUT,
    ):
        await model._process_event(message={"id": "digitalOutput", "value": 3})

        assert model.system_status["isPowerCommunicationOn"] is True
        assert model.system_status["isPowerMotorOn"] is True

    with qtbot.waitSignal(
        model.utility_monitor.signal_utility.digital_status_input, timeout=TIMEOUT
    ):
        await model._process_event(message={"id": "digitalInput", "value": 1})

    with qtbot.waitSignal(model.signal_config.config, timeout=TIMEOUT):
        await model._process_event(
            message={
                "id": "config",
                "configuration": "surrogate_handling.csv",
                "version": "20180831T092556",
                "controlParameters": "CtrlParameterFiles_surg",
                "lutParameters": "FinalHandlingLUTs",
                "powerWarningMotor": 5.0,
                "powerFaultMotor": 10.0,
                "powerThresholdMotor": 20.0,
                "powerWarningComm": 5.0,
                "powerFaultComm": 10.0,
                "powerThresholdComm": 10.0,
                "inPositionAxial": 0.158,
                "inPositionTangent": 1.1,
                "inPositionSample": 1.0,
                "timeoutSal": 15.0,
                "timeoutCrio": 1.0,
                "timeoutIlc": 3,
                "inclinometerDelta": 2.0,
                "inclinometerDiffEnabled": True,
                "cellTemperatureDelta": 2.0,
            }
        )

    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        await model._process_event(message={"id": "openLoopMaxLimit", "status": True})

    with qtbot.waitSignal(
        model.fault_manager.signal_limit_switch.type_name_status, timeout=TIMEOUT
    ):
        await model._process_event(
            message={"id": "limitSwitchStatus", "retract": [1, 2], "extend": []}
        )

    with qtbot.waitSignal(model.signal_power_system.is_state_updated, timeout=TIMEOUT):
        await model._process_event(
            message={
                "id": "powerSystemState",
                "powerType": 1,
                "status": False,
                "state": 1,
            }
        )

    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        await model._process_event(
            message={"id": "tcpIpConnected", "isConnected": True}
        )

    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        await model._process_event(message={"id": "interlock", "state": True})

    with qtbot.waitSignal(model.signal_status.name_status, timeout=TIMEOUT):
        await model._process_event(
            message={"id": "cellTemperatureHiWarning", "hiWarning": True}
        )

    with qtbot.waitSignal(model.signal_control.is_control_updated, timeout=TIMEOUT):
        await model._process_event(
            message={"id": "inclinationTelemetrySource", "source": 2}
        )
    assert model.inclination_source == MTM2.InclinationTelemetrySource.MTMOUNT

    with qtbot.waitSignal(model.signal_ilc_status.address_mode, timeout=TIMEOUT):
        await model._process_event(
            message={"id": "innerLoopControlMode", "address": 1, "mode": 2}
        )

    with qtbot.waitSignal(
        model.fault_manager.signal_error.summary_faults_status, timeout=TIMEOUT
    ):
        await model._process_event(message={"id": "summaryFaultsStatus", "status": 10})

    with qtbot.waitSignal(
        model.fault_manager.signal_error.enabled_faults_mask, timeout=TIMEOUT
    ):
        await model._process_event(message={"id": "enabledFaultsMask", "mask": 10})

    with qtbot.waitSignal(model.signal_config.files, timeout=TIMEOUT):
        await model._process_event(
            message={"id": "configurationFiles", "files": ["a", "b"]}
        )

    with qtbot.waitSignal(model.signal_config.temperature_offset, timeout=TIMEOUT):
        await model._process_event(
            message={
                "id": "temperatureOffset",
                "ring": [21.0] * NUM_TEMPERATURE_RING,
                "intake": [0.0] * NUM_TEMPERATURE_INTAKE,
                "exhaust": [0.0] * NUM_TEMPERATURE_EXHAUST,
            }
        )


def test_get_message_name(model: Model) -> None:
    assert model._get_message_name("") == ""
    assert model._get_message_name(dict()) == ""

    assert model._get_message_name({"id": "test"}) == "test"


def test_process_telemetry(qtbot: QtBot, model: Model) -> None:
    with qtbot.waitSignal(
        model.utility_monitor.signal_position.position, timeout=TIMEOUT
    ):
        model._process_telemetry(
            message={
                "id": "position",
                "x": 1,
                "y": 1,
                "z": 1,
                "xRot": 1,
                "yRot": 1,
                "zRot": 1,
            }
        )

    with qtbot.waitSignal(
        model.utility_monitor.signal_position.position_ims, timeout=TIMEOUT
    ):
        model._process_telemetry(
            message={
                "id": "positionIMS",
                "x": 1,
                "y": 1,
                "z": 1,
                "xRot": 1,
                "yRot": 1,
                "zRot": 1,
            }
        )

    model.utility_monitor.hard_points["axial"] = [6, 16, 26]
    num_axial = NUM_ACTUATOR - NUM_TANGENT_LINK
    with qtbot.waitSignal(
        model.utility_monitor.signal_detailed_force.forces_axial, timeout=TIMEOUT
    ):
        model._process_telemetry(
            message={
                "id": "axialForce",
                "lutGravity": [1] * num_axial,
                "lutTemperature": [1] * num_axial,
                "applied": [1] * num_axial,
                "measured": [1] * num_axial,
                "hardpointCorrection": [1] * num_axial,
            }
        )

    model.utility_monitor.hard_points["tangent"] = [74, 76, 78]
    with qtbot.waitSignal(
        model.utility_monitor.signal_detailed_force.forces_tangent, timeout=TIMEOUT
    ):
        model._process_telemetry(
            message={
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
            message={
                "id": "temperature",
                "intake": [1] * 2,
                "exhaust": [1] * 2,
                "ring": [1] * 12,
            }
        )

    with qtbot.waitSignals(
        [
            model.utility_monitor.signal_utility.inclinometer_raw,
            model.utility_monitor.signal_utility.inclinometer_processed,
        ],
        timeout=TIMEOUT,
    ):
        model._process_telemetry(
            message={
                "id": "zenithAngle",
                "inclinometerRaw": 1,
                "inclinometerProcessed": 1,
            }
        )

    with qtbot.waitSignal(
        model.utility_monitor.signal_utility.inclinometer_tma, timeout=TIMEOUT
    ):
        model._process_telemetry(
            message={
                "id": "inclinometerAngleTma",
                "inclinometer": 1,
            }
        )

    model._process_telemetry(
        message={
            "id": "axialEncoderPositions",
            "position": [10000] * num_axial,
        }
    )
    assert model.utility_monitor.forces_axial.position_in_mm == [10] * num_axial

    model._process_telemetry(
        message={
            "id": "tangentEncoderPositions",
            "position": [10000] * NUM_TANGENT_LINK,
        }
    )
    assert (
        model.utility_monitor.forces_tangent.position_in_mm == [10] * NUM_TANGENT_LINK
    )

    with qtbot.waitSignal(
        model.utility_monitor.signal_utility.displacements, timeout=TIMEOUT
    ):
        num_sensor = 6
        model._process_telemetry(
            message={
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
            message={
                "id": "powerStatus",
                "motorVoltage": 1,
                "motorCurrent": 1,
                "commVoltage": 1,
                "commCurrent": 1,
            }
        )

    with qtbot.waitSignals(
        [
            model.utility_monitor.signal_utility.power_motor_raw,
            model.utility_monitor.signal_utility.power_communication_raw,
        ],
        timeout=TIMEOUT,
    ):
        num_sensor = 6
        model._process_telemetry(
            message={
                "id": "powerStatusRaw",
                "motorVoltage": 1,
                "motorCurrent": 1,
                "commVoltage": 1,
                "commCurrent": 1,
            }
        )

    with qtbot.waitSignal(
        model.utility_monitor.signal_detailed_force.force_error_tangent, timeout=TIMEOUT
    ):
        model._process_telemetry(
            message={
                "id": "forceErrorTangent",
                "force": [1] * NUM_TANGENT_LINK,
                "weight": 1,
                "sum": 1,
            }
        )


def test_check_force_with_limit(qtbot: QtBot, model: Model) -> None:
    model.utility_monitor.forces_axial.f_cur = [1000.0] * (
        NUM_ACTUATOR - NUM_TANGENT_LINK
    )

    with qtbot.waitSignal(
        model.fault_manager.signal_limit_switch.type_name_status, timeout=TIMEOUT
    ):
        model._check_force_with_limit()


def test_get_current_force_limits(model: Model) -> None:
    # Check the open-loop
    (
        limit_force_axial,
        limit_force_tangent,
    ) = model.get_current_force_limits()

    assert limit_force_axial == LIMIT_FORCE_AXIAL_OPEN_LOOP
    assert limit_force_tangent == LIMIT_FORCE_TANGENT_OPEN_LOOP

    # Check the open-loop maximum
    model.system_status["isOpenLoopMaxLimitsEnabled"] = True
    (
        limit_force_axial,
        limit_force_tangent,
    ) = model.get_current_force_limits()

    assert limit_force_axial == MAX_LIMIT_FORCE_AXIAL_OPEN_LOOP
    assert limit_force_tangent == MAX_LIMIT_FORCE_TANGENT_OPEN_LOOP

    # Check the closed-loop
    model.is_closed_loop = True
    (
        limit_force_axial,
        limit_force_tangent,
    ) = model.get_current_force_limits()

    assert limit_force_axial == LIMIT_FORCE_AXIAL_CLOSED_LOOP
    assert limit_force_tangent == LIMIT_FORCE_TANGENT_CLOSED_LOOP


def test_process_lost_connection(model: Model) -> None:
    model.system_status["isCrioConnected"] = True
    model.system_status["isTelemetryActive"] = True

    model._process_lost_connection()

    assert model.system_status["isCrioConnected"] is False
    assert model.system_status["isTelemetryActive"] is False


@pytest.mark.asyncio
async def test_state_transition_normal(model_async: Model) -> None:
    await model_async.enter_diagnostic()
    assert model_async.local_mode == LocalMode.Diagnostic

    await model_async.enter_enable()
    assert model_async.local_mode == LocalMode.Enable

    await model_async.exit_enable()
    assert model_async.local_mode == LocalMode.Diagnostic

    await model_async.exit_diagnostic()
    assert model_async.local_mode == LocalMode.Standby


@pytest.mark.asyncio
async def test_fault(model_async: Model) -> None:
    await model_async.enter_diagnostic()
    await model_async.enter_enable()

    await model_async.fault()
    assert model_async.local_mode == LocalMode.Diagnostic
