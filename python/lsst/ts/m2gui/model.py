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

__all__ = ["Model"]

import asyncio
import logging
import types
import typing

import numpy as np
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
    ActuatorDisplacementUnit,
    ClosedLoopControlMode,
    CommandActuator,
    CommandScript,
    ControllerCell,
    DigitalInput,
    DigitalOutput,
    DigitalOutputStatus,
    LimitSwitchType,
    MockErrorCode,
    PowerType,
    check_limit_switches,
    get_config_dir,
)

from .config import Config
from .enums import (
    DisplacementSensorDirection,
    LocalMode,
    Ring,
    Status,
    TemperatureGroup,
)
from .fault_manager import FaultManager
from .force_error_tangent import ForceErrorTangent
from .signals import (
    SignalConfig,
    SignalControl,
    SignalIlcStatus,
    SignalPowerSystem,
    SignalScript,
    SignalStatus,
)
from .utility_monitor import UtilityMonitor
from .utils import get_num_actuator_ring, map_actuator_id_to_alias


class Model(object):
    """Model class of the application.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.
    host : `str`, optional
        Host address. (the default is "localhost")
    port_command : `int`, optional
        Command port to connect. (the default is 50010)
    port_telemetry : `int`, optional
        Telemetry port to connect. (the default is 50011)
    timeout_connection : `float`, optional
        Connection timeout in second. (the default is 10.0)
    timeout_in_second : `float`, optional
        Time limit for reading data from the TCP/IP interface (sec). (the
        default is 0.05)
    is_simulation_mode: `bool`, optional
        True if running in simulation mode. (the default is False)

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    is_csc_commander : `bool`
        Commandable SAL component (CSC) is the commander or not.
    local_mode : enum `LocalMode`
        Local model.
    is_closed_loop : `bool`
        Closed-loop control is on or not.
    inclination_source : enum `MTM2.InclinationTelemetrySource`
        Inclination telemetry source.
    signal_control : `SignalControl`
        Signal to report the control status.
    signal_power_system : `SignalPowerSystem`
        Signal to report the power system status.
    signal_status : `SignalStatus`
        Signal to report the updated status of system.
    signal_config : `SignalConfig`
        Signal to send the configuration.
    signal_script : `SignalScript`
        Signal to send the script progress.
    signal_ilc_status : `SignalIlcStatus`
        Signal to send the inner-loop controller (ILC) status.
    system_status : `dict`
        System status.
    fault_manager : `FaultManager`
        Fault manager to record the system error.
    utility_monitor : `UtilityMonitor`
        Utility monitor to monitor the utility status.
    controller : `lsst.ts.m2com.ControllerCell`
        Controller to do the TCP/IP communication with the servers of M2 cell.
    duration_refresh : `int`
        Duration to refresh the data in milliseconds.
    """

    def __init__(
        self,
        log: logging.Logger,
        host: str = "localhost",
        port_command: int = 50010,
        port_telemetry: int = 50011,
        timeout_connection: float = 10.0,
        timeout_in_second: float = 0.05,
        is_simulation_mode: bool = False,
    ) -> None:
        self.log = log

        self.is_csc_commander = False
        self.local_mode = LocalMode.Standby
        self.is_closed_loop = False
        self.inclination_source = MTM2.InclinationTelemetrySource.ONBOARD

        self.signal_control = SignalControl()
        self.signal_power_system = SignalPowerSystem()
        self.signal_status = SignalStatus()
        self.signal_config = SignalConfig()
        self.signal_script = SignalScript()
        self.signal_ilc_status = SignalIlcStatus()

        self.system_status = self._set_system_status()

        self.fault_manager = FaultManager(
            self.get_actuator_default_status(Status.Normal)
        )
        self.utility_monitor = UtilityMonitor()

        self.controller = ControllerCell(
            log=self.log,
            timeout_in_second=timeout_in_second,
            is_csc=False,
            host=host,
            port_command=port_command,
            port_telemetry=port_telemetry,
            timeout_connection=timeout_connection,
        )

        self._is_simulation_mode = is_simulation_mode

        self.duration_refresh = 100

    def _set_system_status(self) -> dict[str, bool]:
        """Set the default system status.

        Returns
        -------
        system_status : `dict`
            Default system status.
        """

        system_status = {
            "isCrioConnected": False,
            "isTelemetryActive": False,
            "isInPosition": False,
            "isPowerCommunicationOn": False,
            "isPowerMotorOn": False,
            "isOpenLoopMaxLimitsEnabled": False,
            "isAlarmOn": False,
            "isWarningOn": False,
            "isInterlockEnabled": False,
            "isCellTemperatureHigh": False,
        }

        return system_status

    def get_actuator_default_status(self, status: typing.Any) -> dict:
        """Get the default actuator status.

        Parameters
        ----------
        status : `any`
            Default status.

        Returns
        -------
        collection : `dict`
            Collection of default actuator status.
        """

        collection: dict = dict()
        collection = self._set_actuator_default_status_specific_ring(
            Ring.B, collection, status
        )
        collection = self._set_actuator_default_status_specific_ring(
            Ring.C, collection, status
        )
        collection = self._set_actuator_default_status_specific_ring(
            Ring.D, collection, status
        )
        collection = self._set_actuator_default_status_specific_ring(
            Ring.A, collection, status
        )

        return collection

    def _set_actuator_default_status_specific_ring(
        self, ring: Ring, collection: dict, status: typing.Any
    ) -> dict:
        """Set the default actuator status in specific ring.

        Parameters
        ----------
        ring : enum `Ring`
            Name of ring.
        collection : `dict`
            Collection of actuator status.
        status : `any`
            Default status.

        Returns
        -------
        collection : `dict`
            Updated collection.
        """

        number = get_num_actuator_ring(ring)
        for idx in range(1, number + 1):
            name = ring.name + str(idx)
            collection[name] = status

        return collection

    def report_control_status(self) -> None:
        """Report the control status."""
        self.signal_control.is_control_updated.emit(True)

    def report_error(self, error: int) -> None:
        """Report the error.

        Parameters
        ----------
        error : `int`
            Error code.
        """

        self.fault_manager.add_error(error)
        self._check_error_and_update_status()

    def _check_error_and_update_status(self) -> None:
        """Check whenever the error is triggered, and update the related
        internal status."""

        is_error_on = self.controller.error_handler.exists_error()
        self.update_system_status("isAlarmOn", is_error_on)

        is_warning_on = self.controller.error_handler.exists_warning()
        self.update_system_status("isWarningOn", is_warning_on)

    def clear_error(self, error: int) -> None:
        """Clear the error.

        Parameters
        ----------
        error : `int`
            Error code.
        """

        self.fault_manager.clear_error(error)
        self._check_error_and_update_status()

    async def reset_errors(self) -> None:
        """Reset errors."""

        self.fault_manager.reset_errors()
        self.fault_manager.reset_limit_switch_status(LimitSwitchType.Retract)
        self.fault_manager.reset_limit_switch_status(LimitSwitchType.Extend)

        await self.controller.clear_errors(bypass_state_checking=True)

        self._check_error_and_update_status()

    async def enable_open_loop_max_limit(self, status: bool) -> None:
        """Enable the maximum limit in open-loop control.

        Parameters
        ----------
        status : `bool`
            Enable the maximum limit or not.

        Raises
        ------
        `RuntimeError`
            Not in the open-loop control.
        """

        if not self.is_closed_loop:
            await self.controller.write_command_to_server(
                "enableOpenLoopMaxLimit", message_details={"status": status}
            )
        else:
            raise RuntimeError(
                "Failed to enable the maximum limit. Only allow in open-loop control."
            )

    def update_system_status(self, status_name: str, new_status: bool) -> None:
        """Update the system status.

        Parameters
        ----------
        status_name : `str`
            Status name. It must be in the keys of self.system_status.
        new_status : `bool`
            New status.

        Raises
        ------
        `ValueError`
            Status name is not in the list.
        """

        if status_name in self.system_status.keys():
            if self.system_status[status_name] != new_status:
                self.system_status[status_name] = new_status
                self.signal_status.name_status.emit((status_name, new_status))
        else:
            raise ValueError(
                f"{status_name} not in the {list(self.system_status.keys())}."
            )

    def report_config(self, **kwargs: dict[str, typing.Any]) -> Config:
        """Report the configuration defined in `Config` class.

        Parameters
        ----------
        **kwargs : `dict`
            Configuration key-value pairs. The available keys are defined in
            `Config` class.

        Returns
        -------
        config : `Config`
            Configuration.

        Raises
        ------
        `KeyError`
            Key name does not exist in the Config class.
        """

        config = Config()
        for name, value in kwargs.items():
            if hasattr(config, name):
                setattr(config, name, value)
            else:
                raise KeyError(f"{name} does not exist in the Config class.")

        self.signal_config.config.emit(config)

        return config

    def report_script_progress(self, progress: int) -> None:
        """Report the script progress.

        Parameters
        ----------
        progress : `int`
            Progress of the script execution (0-100%).
        """
        self.signal_script.progress.emit(int(progress))

    async def save_position(self) -> None:
        """Save the rigid body position."""
        await self.controller.write_command_to_server("saveMirrorPosition")

    async def go_to_position(
        self, x: float, y: float, z: float, rx: float, ry: float, rz: float
    ) -> None:
        """Go to the position.

        Parameters
        ----------
        x : `float`
            Position x in um.
        y : `float`
            Position y in um.
        z : `float`
            Position z in um.
        rx : `float`
            Rotation x in arcsec.
        ry : `float`
            Rotation y in arcsec.
        rz : `float`
            Rotation z in arcsec.

        Raises
        ------
        `RuntimeError`
            Not in the closed-loop control.
        """

        if self.is_enabled_and_closed_loop_control():
            await self.controller.position_mirror(x, y, z, rx, ry, rz)
        else:
            raise RuntimeError("Mirror can be positioned only in closed-loop control.")

    def is_enabled_and_open_loop_control(self) -> bool:
        """The system is in the Enabled state and open-loop control or not.

        Returns
        -------
        `bool`
            True if the system is in the Enabled state and open-loop control.
            Otherwise, False.
        """
        return self.local_mode == LocalMode.Enable and not self.is_closed_loop

    def is_enabled_and_closed_loop_control(self) -> bool:
        """The system is in the Enabled state and closed-loop control or not.

        Returns
        -------
        `bool`
            True if the system is in the Enabled state and closed-loop control.
            Otherwise, False.
        """
        return self.local_mode == LocalMode.Enable and self.is_closed_loop

    async def set_home(self) -> None:
        """Set the home position."""
        await self.controller.write_command_to_server("setMirrorHome")

    async def reboot_controller(self) -> None:
        """Reboot the cell controller.

        Raises
        ------
        `RuntimeError`
            Not in the standby state with local control.
        """

        if self.local_mode == LocalMode.Standby and not self.is_csc_commander:
            await self.controller.write_command_to_server("rebootController")
        else:
            raise RuntimeError(
                "Controller can only be rebooted at the standby state with local control."
            )

    async def set_bit_digital_status(
        self,
        idx: int,
        status: DigitalOutputStatus,
    ) -> None:
        """Set the bit value of digital status.

        Parameters
        ----------
        idx : `int`
            Bit index that begins from 0, which should be >= 0.
        status : enum `lsst.ts.m2com.DigitalOutputStatus`
            Digital output status.
        """

        await self.controller.write_command_to_server(
            "switchDigitalOutput",
            message_details={"bit": 2**idx, "status": int(status)},
        )

    async def command_script(
        self, command: CommandScript, script_name: str | None = None
    ) -> None:
        """Run the script command.

        Parameters
        ----------
        command : enum `lsst.ts.m2com.CommandScript`
            Script command.
        script_name : `str` or None, optional
            Name of the script. (the default is None)

        Raises
        ------
        `RuntimeError`
            Not in the enabled state.
        """

        if self.local_mode == LocalMode.Enable:
            message_details = {"scriptCommand": command}
            if script_name is not None:
                message_details["scriptName"] = script_name

            await self.controller.write_command_to_server(
                "runScript",
                message_details=message_details,
            )

        else:
            raise RuntimeError(
                "Failed to run the script command. Only allowed in Enabled state."
            )

    async def command_actuator(
        self,
        command: CommandActuator,
        actuators: list[int] | None = None,
        target_displacement: float | int = 0,
        unit: ActuatorDisplacementUnit = ActuatorDisplacementUnit.Millimeter,
    ) -> None:
        """Run the actuator command.

        Parameters
        ----------
        command : enum `lsst.ts.m2com.CommandActuator`
            Actuator command.
        actuators : `list [int]` or None, optional
            Selected actuators to do the movement. If the empty list [] is
            passed, the function will raise the RuntimeError. (the default is
            None)
        target_displacement : `float` or `int`, optional
            Target displacement of the actuators. (the default is 0)
        unit : enum `lsst.ts.m2com.ActuatorDisplacementUnit`, optional
            Displacement unit. (the default is
            ActuatorDisplacementUnit.Millimeter)

        Raises
        ------
        `RuntimeError`
            No actuator is selected.
        `RuntimeError`
            Not in the enabled state with open-loop control.
        """

        if (actuators is not None) and (len(actuators) == 0):
            raise RuntimeError("No actuator is selected.")

        if unit == ActuatorDisplacementUnit.Step:
            target_displacement = int(target_displacement)

        if self.is_enabled_and_open_loop_control():
            message_details = {"actuatorCommand": command}
            if actuators is not None:
                message_details.update(
                    {
                        "actuators": actuators,
                        "displacement": target_displacement,
                        "unit": unit,
                    }
                )

            await self.controller.write_command_to_server(
                "moveActuators",
                message_details=message_details,
            )

        else:
            raise RuntimeError(
                "Failed to command the actuator. Only allow in Enabled state and open-loop control."
            )

    async def apply_actuator_force(self, actuators: list[int], force: float) -> None:
        """Apply the actuator force.

        Parameters
        ----------
        actuators : `list`
            Selected actuators to do the movement. If the empty list [] is
            passed, the function will raise the RuntimeError.
        force : `float`
            Force to apply in Newton.

        Raises
        ------
        `RuntimeError`
            No actuator is selected.
        `RuntimeError`
            Not in the enabled state with closed-loop control.
        """

        if len(actuators) == 0:
            raise RuntimeError("No actuator is selected.")

        if self.is_enabled_and_closed_loop_control():
            # Prepare the applied forces
            num_axial = NUM_ACTUATOR - NUM_TANGENT_LINK
            force_axial = [0.0] * num_axial
            force_tangent = [0.0] * NUM_TANGENT_LINK

            for actuator in actuators:
                if actuator < num_axial:
                    force_axial[actuator] = force
                else:
                    force_tangent[actuator - num_axial] = force

            # Apply the forces
            await self.controller.apply_forces(force_axial, force_tangent)

        else:
            raise RuntimeError(
                "Failed to command the actuator. Only allow in Enabled state and closed-loop control."
            )

    async def reset_breakers(self, power_type: PowerType) -> None:
        """Reset the breakers.

        Parameters
        ----------
        power_type : enum `lsst.ts.m2com.PowerType`
            Power type.
        """

        self.utility_monitor.reset_breakers(power_type)

        await self.controller.write_command_to_server(
            "resetBreakers", message_details={"powerType": power_type}
        )

    def update_connection_information(
        self,
        host: str,
        port_command: int,
        port_telemetry: int,
        timeout_connection: float,
    ) -> None:
        """Update the connection information.

        Parameters
        ----------
        host : `str`
            Host address.
        port_command : `int`
            Command port to connect.
        port_telemetry : `int`
            Telemetry port to connect.
        timeout_connection : `float`
            Connection timeout in second.

        Raises
        ------
        `RuntimeError`
            There is the connection with the M2 controller already.
        `ValueError`
            When the command port equals to the telemetry port.
        """

        if self.system_status["isCrioConnected"]:
            raise RuntimeError("Please disconnect from the M2 controller first.")

        if port_command == port_telemetry:
            raise ValueError("Command port should be different from telemetry port.")

        self.controller.host = host
        self.controller.port_command = port_command
        self.controller.port_telemetry = port_telemetry
        self.controller.timeout_connection = timeout_connection

    async def connect(self, time_process: float = 3.0) -> None:
        """Connect to the M2 controller.

        Parameters
        ----------
        time_process : `float`, optional
            Waiting time to let the application processes the received welcome
            messages. (the default is 3.0)

        Raises
        ------
        `RuntimeError`
            There is the connection with the M2 controller already.
        """

        if self.system_status["isCrioConnected"]:
            raise RuntimeError("Please disconnect from the M2 controller first.")

        self.log.info("Connecting to the M2 controller...")

        # Run the mock server in the simulation mode
        if self._is_simulation_mode:
            await self.controller.run_mock_server(get_config_dir(), "harrisLUT")

        # Run the event and telemetry loops
        if self.controller.run_loops is False:
            self.controller.run_loops = True

            self.log.debug(
                "Starting event, telemetry and connection monitor loop tasks."
            )

            self.controller.start_task_event_loop(self._process_event)
            self.controller.start_task_telemetry_loop(self._process_telemetry)
            self.controller.start_task_connection_monitor_loop(
                self._process_lost_connection
            )

        await self.controller.connect_server()

        # Wait some time to process the welcome messages
        await asyncio.sleep(time_process)

        # Clear all the existed error if any
        if self.fault_manager.has_error():
            await self.reset_errors()

    async def _process_event(self, message: dict | None = None) -> None:
        """Process the events from the M2 controller.

        Parameters
        ----------
        message : `dict` or None, optional
            Message from the M2 controller. (the default is None)
        """

        name = self._get_message_name(message)

        if name != "" and message is not None:
            if name == "m2AssemblyInPosition":
                self.update_system_status("isInPosition", message["inPosition"])

            elif name == "errorCode":
                error_code = message["errorCode"]
                self.report_error(error_code)

                self.log.warning(f"Receive the error code: {error_code}.")

            elif name == "commandableByDDS":
                self.is_csc_commander = message["state"]
                self.report_control_status()

                self.log.info(
                    f"M2 controller is commandable by CSC: {self.is_csc_commander}."
                )

            elif name == "hardpointList":
                hardpoints = message["actuators"]
                # The first 3 actuators are the axial actuators. The latters
                # are the tangent links.
                self.utility_monitor.update_hard_points(hardpoints[:3], hardpoints[3:])

            elif name == "forceBalanceSystemStatus":
                self.is_closed_loop = message["status"]
                self.report_control_status()

                self.log.info(
                    f"Status of the force balance system: {self.is_closed_loop}."
                )

            elif name == "scriptExecutionStatus":
                self.report_script_progress(int(message["percentage"]))

            elif name == "digitalOutput":
                digital_output = message["value"]
                self.utility_monitor.update_digital_status_output(digital_output)

                self.update_system_status(
                    "isPowerCommunicationOn",
                    bool(digital_output & DigitalOutput.CommunicationPower.value),
                )
                self.update_system_status(
                    "isPowerMotorOn",
                    bool(digital_output & DigitalOutput.MotorPower.value),
                )

            elif name == "digitalInput":
                digital_input = message["value"]
                self.utility_monitor.update_digital_status_input(digital_input)
                self._update_breaker(digital_input)

            elif name == "config":
                self.report_config(
                    file_configuration=message["configuration"],
                    file_version=message["version"],
                    file_control_parameters=message["controlParameters"],
                    file_lut_parameters=message["lutParameters"],
                    power_warning_motor=message["powerWarningMotor"],
                    power_fault_motor=message["powerFaultMotor"],
                    power_threshold_motor=message["powerThresholdMotor"],
                    power_warning_communication=message["powerWarningComm"],
                    power_fault_communication=message["powerFaultComm"],
                    power_threshold_communication=message["powerThresholdComm"],
                    in_position_axial=message["inPositionAxial"],
                    in_position_tangent=message["inPositionTangent"],
                    in_position_sample=message["inPositionSample"],
                    timeout_sal=message["timeoutSal"],
                    timeout_crio=message["timeoutCrio"],
                    timeout_ilc=message["timeoutIlc"],
                    misc_range_angle=message["inclinometerDelta"],
                    misc_diff_enabled=message["inclinometerDiffEnabled"],
                    misc_range_temperature=message["cellTemperatureDelta"],
                )

            elif name == "openLoopMaxLimit":
                isOpenLoopMaxLimitsEnabled = message["status"]
                self.update_system_status(
                    "isOpenLoopMaxLimitsEnabled", isOpenLoopMaxLimitsEnabled
                )

                self.log.info(
                    f"Open-loop maximum limit is enabled: {isOpenLoopMaxLimitsEnabled}."
                )

            elif name == "limitSwitchStatus":
                if len(message["retract"]) != 0:
                    self._report_triggered_limit_switch(
                        LimitSwitchType.Retract,
                        message["retract"],
                        is_hardware_fault=True,
                    )

                    self.log.info(
                        f"{LimitSwitchType.Retract!r} limit switches triggered: {message['retract']}."
                    )

                if len(message["extend"]) != 0:
                    self._report_triggered_limit_switch(
                        LimitSwitchType.Extend,
                        message["extend"],
                        is_hardware_fault=True,
                    )

                    self.log.info(
                        f"{LimitSwitchType.Extend!r} limit switches triggered: {message['extend']}."
                    )

            elif name == "powerSystemState":
                self.signal_power_system.is_state_updated.emit(True)

            elif name == "closedLoopControlMode":
                self.log.info(
                    f"Closed-loop control mode: {self.controller.closed_loop_control_mode!r}."
                )

            elif name == "tcpIpConnected":
                self.update_system_status("isCrioConnected", message["isConnected"])

            elif name == "interlock":
                self.update_system_status("isInterlockEnabled", message["state"])

            elif name == "cellTemperatureHiWarning":
                self.update_system_status("isCellTemperatureHigh", message["hiWarning"])

            elif name == "inclinationTelemetrySource":
                self.inclination_source = MTM2.InclinationTelemetrySource(
                    message["source"]
                )
                self.report_control_status()

                self.log.info(f"Inclination source: {self.inclination_source!r}.")

            elif name == "innerLoopControlMode":
                self._report_ilc_status(message["address"], message["mode"])

            elif name == "summaryFaultsStatus":
                status = int(message["status"])
                self.fault_manager.update_summary_faults_status(status)

                self.log.info(f"Summary faults status: {hex(status)}.")

            elif name == "enabledFaultsMask":
                mask = int(message["mask"])
                self.fault_manager.report_enabled_faults_mask(mask)

                self.log.info(f"Enabled faults mask: {hex(mask)}.")

            elif name == "configurationFiles":
                files = message["files"]
                self.signal_config.files.emit(files)

                self.log.info(f"Available configuration files: {files}.")

            elif name == "temperatureOffset":
                offset_ring = message["ring"]

                # Need to fix this event in ts_xml in the future. The offset
                # is a constant instead of an array.
                self.signal_config.temperature_offset.emit(float(offset_ring[0]))

                self.log.info(f"Ring temperature offset: {offset_ring}.")

            # Ignore these messages because they are specific to CSC
            elif name in (
                "summaryState",
                "detailedState",
            ):
                pass

            else:
                self.log.warning(f"Unspecified event message: {name}, ignoring...")

        # Fault the system if needed
        await self._check_and_fault_system()

    def _get_message_name(self, message: dict | None) -> str:
        """Get the name of message.

        Parameters
        ----------
        message : `dict` or `None`
            Message.

        Returns
        -------
        `str`
            Name of the message. If there is no 'id' field, return the empty
            string.
        """

        if message is None:
            return ""

        try:
            return message["id"]
        except (TypeError, KeyError):
            return ""

    def _update_breaker(self, digital_input: int) -> None:
        """Update the breakers.

        Parameters
        ----------
        digital_input : `int`
            Digital input.
        """

        # Note the enum_items should have the same order as
        # self.utility_monitor.breakers
        enum_items = []
        for item in DigitalInput:
            if "PowerBreaker" in item.name:
                enum_items.append(item)

        for item, enum_item in zip(self.utility_monitor.breakers.keys(), enum_items):
            self.utility_monitor.update_breaker(
                item, not (digital_input & enum_item.value)
            )

    def _report_triggered_limit_switch(
        self,
        limit_switch_type: LimitSwitchType,
        limit_switches: list[int],
        is_hardware_fault: bool = True,
    ) -> None:
        """Report the triggered limit switch.

        Parameters
        ----------
        limit_switch_type : enum `lsst.ts.m2com.LimitSwitchType`
            Type of limit switch.
        limit_switches : `list`
            Triggered limit switches.
        is_hardware_fault : `bool`, optional
            Is the hardware fault or not. (the default is True)
        """

        limit_switch_status_current = (
            self.fault_manager.limit_switch_status_retract
            if limit_switch_type == LimitSwitchType.Retract
            else self.fault_manager.limit_switch_status_extend
        )
        status_new = Status.Error if is_hardware_fault else Status.Alert
        try:
            for limit_switch in limit_switches:
                # Check the current status
                ring, number = map_actuator_id_to_alias(limit_switch)
                name = ring.name + str(number)
                status_current = limit_switch_status_current[name]

                # Alert status can not overwrite the error status
                if (status_current == Status.Error) and (status_new == Status.Alert):
                    continue

                # Update the new status
                self.fault_manager.update_limit_switch_status(
                    limit_switch_type, ring, number, status_new
                )

        except ValueError:
            self.log.exception("Unknown limit switches encountered.")

    def _report_ilc_status(self, address: int, mode: int) -> None:
        """Report the status of inner-loop controller (ILC).

        Parameters
        ----------
        address : `int`
            0-based address.
        mode : `int`
            Inner-loop control mode.
        """
        self.signal_ilc_status.address_mode.emit((address, mode))

    async def _check_and_fault_system(self) -> None:
        """Check the system condition and fault the system if needed."""

        # Note some error code might be just the warning. Therefore, we
        # let the error_handler to judge and fault the system when
        # needed.
        error_handler = self.controller.error_handler
        if error_handler.exists_error() or error_handler.has_warning(
            MockErrorCode.LimitSwitchTriggeredOpenloop.value
        ):
            await self.fault()

    def _process_telemetry(self, message: dict | None = None) -> None:
        """Process the telemetry from the M2 controller.

        Parameters
        ----------
        message : `dict` or None, optional
            Message from the M2 controller. (the default is None)
        """

        name = self._get_message_name(message)

        if name != "" and message is not None:
            self.update_system_status("isTelemetryActive", True)

            num_axial = NUM_ACTUATOR - NUM_TANGENT_LINK

            if name == "position":
                self.utility_monitor.update_position(
                    message["x"],
                    message["y"],
                    message["z"],
                    message["xRot"],
                    message["yRot"],
                    message["zRot"],
                    is_ims=False,
                )

            elif name == "positionIMS":
                self.utility_monitor.update_position(
                    message["x"],
                    message["y"],
                    message["z"],
                    message["xRot"],
                    message["yRot"],
                    message["zRot"],
                    is_ims=True,
                )

            elif name == "axialForce":
                forces_axial = self.utility_monitor.get_forces_axial()

                forces_axial.f_gravity = message["lutGravity"]
                forces_axial.f_temperature = message["lutTemperature"]
                forces_axial.f_delta = message["applied"]
                forces_axial.f_cur = message["measured"]

                # If the controller has the error, the hardpoint correction
                # will not be calculated.
                if len(message["hardpointCorrection"]) == num_axial:
                    forces_axial.f_hc = message["hardpointCorrection"]

                forces_axial.f_error = [
                    (
                        forces_axial.f_gravity[idx]
                        + forces_axial.f_temperature[idx]
                        + forces_axial.f_delta[idx]
                        + forces_axial.f_hc[idx]
                        - forces_axial.f_cur[idx]
                    )
                    for idx in range(num_axial)
                ]

                # Do not consider the force error in hardpoints.
                # This is the logic in M2 cell LabVIEW code by vendor. Need to
                # figure out why it was designed in this way in a latter time.
                for idx in self.utility_monitor.hard_points["axial"]:
                    # Index begins from 0 in list
                    forces_axial.f_error[idx - 1] = 0

                self.utility_monitor.update_forces_axial(forces_axial)

                self._check_force_with_limit()

            elif name == "tangentForce":
                forces_tangent = self.utility_monitor.get_forces_tangent()

                # There is no temperature LUT correction
                forces_tangent.f_gravity = message["lutGravity"]
                forces_tangent.f_delta = message["applied"]
                forces_tangent.f_cur = message["measured"]

                # If the controller has the error, the hardpoint correction
                # will not be calculated.
                if len(message["hardpointCorrection"]) == NUM_TANGENT_LINK:
                    forces_tangent.f_hc = message["hardpointCorrection"]

                forces_tangent.f_error = [
                    (
                        forces_tangent.f_gravity[idx]
                        + forces_tangent.f_delta[idx]
                        + forces_tangent.f_hc[idx]
                        - forces_tangent.f_cur[idx]
                    )
                    for idx in range(NUM_TANGENT_LINK)
                ]

                # Do not consider the force error in hardpoints.
                # This is the logic in M2 cell LabVIEW code by vendor. Need to
                # figure out why it was designed in this way in a latter time.
                for idx in self.utility_monitor.hard_points["tangent"]:
                    # Index begins from 0 in list
                    forces_tangent.f_error[idx - 1 - num_axial] = 0

                self.utility_monitor.update_forces_tangent(forces_tangent)

                self._check_force_with_limit()

            elif name == "temperature":
                self.utility_monitor.update_temperature(
                    TemperatureGroup.Intake, message["intake"]
                )
                self.utility_monitor.update_temperature(
                    TemperatureGroup.Exhaust, message["exhaust"]
                )

                ring_temperature = message["ring"]
                self.utility_monitor.update_temperature(
                    TemperatureGroup.LG2, ring_temperature[:4]
                )
                self.utility_monitor.update_temperature(
                    TemperatureGroup.LG3, ring_temperature[4:8]
                )
                self.utility_monitor.update_temperature(
                    TemperatureGroup.LG4, ring_temperature[8:]
                )

            elif name == "zenithAngle":
                self.utility_monitor.update_inclinometer_angle(
                    message["inclinometerRaw"],
                    new_angle_processed=message["inclinometerProcessed"],
                )

            elif name == "inclinometerAngleTma":
                self.utility_monitor.update_inclinometer_angle(
                    message["inclinometer"], is_internal=False
                )

            # If the step changes, the position will be changed as well.
            # We base on the change of position to send the "signal" to
            # update the GUI.
            elif name == "axialActuatorSteps":
                self.utility_monitor.forces_axial.step = message["steps"]

            elif name == "tangentActuatorSteps":
                self.utility_monitor.forces_tangent.step = message["steps"]

            elif name == "axialEncoderPositions":
                # The received unit is um instead of mm.
                position = message["position"]
                self.utility_monitor.forces_axial.position_in_mm = [
                    value * 1e-3 for value in position
                ]

            elif name == "tangentEncoderPositions":
                # The received unit is um instead of mm.
                position = message["position"]
                self.utility_monitor.forces_tangent.position_in_mm = [
                    value * 1e-3 for value in position
                ]

            elif name == "displacementSensors":
                self.utility_monitor.update_displacements(
                    DisplacementSensorDirection.Theta, message["thetaZ"]
                )
                self.utility_monitor.update_displacements(
                    DisplacementSensorDirection.Delta, message["deltaZ"]
                )

            elif name == "powerStatus":
                self.utility_monitor.update_power_calibrated(
                    PowerType.Motor, message["motorVoltage"], message["motorCurrent"]
                )
                self.utility_monitor.update_power_calibrated(
                    PowerType.Communication,
                    message["commVoltage"],
                    message["commCurrent"],
                )

            elif name == "powerStatusRaw":
                self.utility_monitor.update_power_raw(
                    PowerType.Motor, message["motorVoltage"], message["motorCurrent"]
                )
                self.utility_monitor.update_power_raw(
                    PowerType.Communication,
                    message["commVoltage"],
                    message["commCurrent"],
                )

            elif name == "forceErrorTangent":
                force_error = ForceErrorTangent()
                force_error.error_force = message["force"]
                force_error.error_weight = message["weight"]
                force_error.error_sum = message["sum"]
                self.utility_monitor.update_force_error_tangent(force_error)

            elif name == "netForcesTotal":
                self.utility_monitor.update_net_force_moment_total(
                    [message[axis] for axis in ("fx", "fy", "fz")], is_force=True
                )

            elif name == "netMomentsTotal":
                self.utility_monitor.update_net_force_moment_total(
                    [message[axis] for axis in ("mx", "my", "mz")], is_force=False
                )

            elif name == "forceBalance":
                self.utility_monitor.update_force_balance(
                    [message[axis] for axis in ("fx", "fy", "fz", "mx", "my", "mz")]
                )

            # Ignore this message because it is specific to CSC
            elif name in ("ilcData"):
                pass

            else:
                self.log.warning(f"Unspecified telemetry message: {name}, ignoring...")

    def _check_force_with_limit(self, buffer: float = 0.05) -> None:
        """Check the measured force with the software limit. If it is out of
        limit, alert the related limit switch status.

        Parameters
        ----------
        buffer : `float`, optional
            Buffer of the force limit in ratio. (the default is 0.05)
        """

        measured_force = np.append(
            self.utility_monitor.forces_axial.f_cur,
            self.utility_monitor.forces_tangent.f_cur,
        )

        limit_force_axial, limit_force_tangent = self.get_current_force_limits()
        ratio = 1 - buffer
        _, limit_switch_retract, limit_switch_extend = check_limit_switches(
            measured_force,
            limit_force_axial * ratio,
            limit_force_tangent * ratio,
        )

        if len(limit_switch_retract) != 0:
            self._report_triggered_limit_switch(
                LimitSwitchType.Retract, limit_switch_retract, is_hardware_fault=False
            )

        if len(limit_switch_extend) != 0:
            self._report_triggered_limit_switch(
                LimitSwitchType.Extend, limit_switch_extend, is_hardware_fault=False
            )

    def get_current_force_limits(self) -> tuple[float, float]:
        """Get the current force limits.

        Returns
        -------
        `float`
            Maximum axial force in Newton.
        `float`
            Maximum tangent force in Newton.
        """

        if self.is_closed_loop:
            return LIMIT_FORCE_AXIAL_CLOSED_LOOP, LIMIT_FORCE_TANGENT_CLOSED_LOOP

        if self.system_status["isOpenLoopMaxLimitsEnabled"] is True:
            return MAX_LIMIT_FORCE_AXIAL_OPEN_LOOP, MAX_LIMIT_FORCE_TANGENT_OPEN_LOOP

        return LIMIT_FORCE_AXIAL_OPEN_LOOP, LIMIT_FORCE_TANGENT_OPEN_LOOP

    def _process_lost_connection(self) -> None:
        """Process the lost of connection from the M2 controller."""

        self.update_system_status("isCrioConnected", False)
        self.update_system_status("isTelemetryActive", False)

    async def enter_diagnostic(self) -> None:
        """Transition from the Standby mode to the Diagnostic mode.

        Raises
        ------
        `RuntimeError`
            When the system is not in the Standby mode.
        """

        if self.local_mode != LocalMode.Standby:
            raise RuntimeError(
                f"System is in {self.local_mode!r} instead of {LocalMode.Standby!r}."
            )

        # Reset motor and communication power breakers bits and cRIO interlock
        # bit. Based on the original developer in ts_mtm2, this is required to
        # make the power system works correctly.
        for idx in range(2, 5):
            await self.set_bit_digital_status(idx, DigitalOutputStatus.BinaryHighLevel)

        # I don't understand why I need to put the CLC mode to be Idle twice.
        # This is translated from the ts_mtm2 and I need this to make the M2
        # cRIO simulator to work.
        await self.controller.set_closed_loop_control_mode(ClosedLoopControlMode.Idle)

        await self.controller.load_configuration()
        await self.controller.set_control_parameters()

        await self.controller.set_closed_loop_control_mode(ClosedLoopControlMode.Idle)
        await self.controller.reset_force_offsets()
        await self.controller.reset_actuator_steps()

        await self.controller.power(PowerType.Communication, True)

        self.local_mode = LocalMode.Diagnostic

    async def enter_enable(self) -> None:
        """Transition from the Diagnostic mode to the Enable mode.

        Raises
        ------
        `RuntimeError`
            When the system is not in the Diagnostic mode.
        """

        if self.local_mode != LocalMode.Diagnostic:
            raise RuntimeError(
                f"System is in {self.local_mode!r} instead of {LocalMode.Diagnostic!r}."
            )

        await self.controller.power(PowerType.Motor, True)
        await self.controller.set_ilc_to_enabled()
        await self.controller.set_closed_loop_control_mode(
            ClosedLoopControlMode.OpenLoop
        )

        self.local_mode = LocalMode.Enable

    async def exit_enable(self) -> None:
        """Transition from the Enable mode to the Diagnostic mode.

        Raises
        ------
        `RuntimeError`
            When the system is not in the Enable mode.
        """

        if self.local_mode != LocalMode.Enable:
            raise RuntimeError(
                f"System is in {self.local_mode!r} instead of {LocalMode.Enable!r}."
            )

        await self._basic_cleanup_and_power_off_motor()
        await self.controller.set_closed_loop_control_mode(ClosedLoopControlMode.Idle)

        self.local_mode = LocalMode.Diagnostic

    async def _basic_cleanup_and_power_off_motor(self) -> None:
        """Basic cleanup and power off the motor."""

        try:
            await self.command_script(CommandScript.Stop)
            await self.command_script(CommandScript.Clear)

            await self.controller.reset_force_offsets()
            await self.controller.reset_actuator_steps()
            await self.controller.set_closed_loop_control_mode(
                ClosedLoopControlMode.TelemetryOnly
            )

            await self.controller.power(PowerType.Motor, False)

        except Exception:
            self.log.exception(
                "Error when doing the basic cleanup and power off the motor."
            )

    async def exit_diagnostic(self) -> None:
        """Transition from the Diagnostic mode to the Standby mode.

        Raises
        ------
        `RuntimeError`
            When the system is not in the Diagnostic mode.
        """

        if self.local_mode != LocalMode.Diagnostic:
            raise RuntimeError(
                f"System is in {self.local_mode!r} instead of {LocalMode.Diagnostic!r}."
            )

        await self.controller.power(PowerType.Communication, False)
        await self.controller.set_closed_loop_control_mode(ClosedLoopControlMode.Idle)

        self.local_mode = LocalMode.Standby

    async def fault(self) -> None:
        """Fault the system and transition to the Diagnostic mode if the
        system is in the Enable mode originally."""

        if self.local_mode == LocalMode.Enable:
            await self._basic_cleanup_and_power_off_motor()

            self.local_mode = LocalMode.Diagnostic

        self.report_control_status()

    async def disconnect(self) -> None:
        """Disconnect from the M2 controller."""

        if self.controller.are_clients_connected():
            self.log.info("Disconnecting from the M2 controller...")
        else:
            self.log.info("No connection with the M2 controller.")

        await self.controller.close_tasks()

        self._process_lost_connection()

    async def __aenter__(self) -> object:
        """This is an overridden function to support the asynchronous context
        manager."""
        return self

    async def __aexit__(
        self,
        type: typing.Type[BaseException] | None,
        value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """This is an overridden function to support the asynchronous context
        manager."""
        await self.controller.close_tasks()
