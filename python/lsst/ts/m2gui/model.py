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

from lsst.ts import salobj
from lsst.ts.m2com import (
    NUM_ACTUATOR,
    NUM_TANGENT_LINK,
    ActuatorDisplacementUnit,
    ControllerCell,
    PowerType,
    get_config_dir,
)

from . import (
    Config,
    DisplacementSensorDirection,
    FaultManager,
    LimitSwitchType,
    LocalMode,
    Ring,
    SignalConfig,
    SignalControl,
    SignalScript,
    SignalStatus,
    TemperatureGroup,
    UtilityMonitor,
    get_num_actuator_ring,
)


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
    timeout_connection : `int` or `float`, optional
        Connection timeout in second. (the default is 10)
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
    signal_control : `SignalControl`
        Signal to report the control status.
    signal_status : `SignalStatus`
        Signal to report the updated status of system.
    signal_config : `SignalConfig`
        Signal to send the configuration.
    signal_script : `SignalScript`
        Signal to send the script progress.
    system_status : `dict`
        System status.
    fault_manager : `FaultManager`
        Fault manager to record the system error.
    utility_monitor : `UtilityMonitor`
        Utility monitor to monitor the utility status.
    controller : `lsst.ts.m2com.ControllerCell`
        Controller to do the TCP/IP communication with the servers of M2 cell.
    """

    def __init__(
        self,
        log,
        host="localhost",
        port_command=50010,
        port_telemetry=50011,
        timeout_connection=10,
        timeout_in_second=0.05,
        is_simulation_mode=False,
    ):

        self.log = log

        self.is_csc_commander = False
        self.local_mode = LocalMode.Standby
        self.is_closed_loop = False

        self.signal_control = SignalControl()
        self.signal_status = SignalStatus()
        self.signal_config = SignalConfig()
        self.signal_script = SignalScript()

        self.system_status = self._set_system_status()

        self.fault_manager = FaultManager(self.get_actuator_default_status(False))
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

    def _set_system_status(self):
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
            "isInMotion": False,
            "isTcsActive": False,
            "isPowerCommunicationOn": False,
            "isPowerMotorOn": False,
            "isOpenLoopMaxLimitsEnabled": False,
            "isAlarmWarningOn": False,
        }

        return system_status

    def get_actuator_default_status(self, status):
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

        collection = dict()
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

    def _set_actuator_default_status_specific_ring(self, ring, collection, status):
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

    def report_control_status(self):
        """Report the control status."""
        self.signal_control.is_control_updated.emit(True)

    def add_error(self, error):
        """Add the error.

        Parameters
        ----------
        error : `int`
            Error code.
        """

        self.fault_manager.add_error(error)
        self._check_error_and_update_status()

    def _check_error_and_update_status(self):
        """Check whenever the error is triggered, and update the related
        internal status."""

        is_error_on = self.fault_manager.has_error()
        self.update_system_status("isAlarmWarningOn", is_error_on)

    def clear_error(self, error):
        """Clear the error.

        Parameters
        ----------
        error : `int`
            Error code.
        """

        self.fault_manager.clear_error(error)
        self._check_error_and_update_status()

    async def reset_errors(self):
        """Reset errors."""

        await self.controller.clear_errors()

        self.fault_manager.reset_errors()
        self.fault_manager.reset_limit_switch_status(LimitSwitchType.Retract)
        self.fault_manager.reset_limit_switch_status(LimitSwitchType.Extend)

        self._check_error_and_update_status()

    async def enable_open_loop_max_limit(self):
        """Enable the maximum limit in open-loop control.

        Raises
        ------
        `RuntimeError`
            Not in the open-loop control.
        """

        if not self.is_closed_loop:
            await self.controller.write_command_to_server("enableOpenLoopMaxLimit")
            self.update_system_status("isOpenLoopMaxLimitsEnabled", True)
        else:
            raise RuntimeError(
                "Failed to enable the maximum limit. Only allow in open-loop control."
            )

    def disable_open_loop_max_limit(self):
        """Disable the maximum limit in open-loop control."""
        self.update_system_status("isOpenLoopMaxLimitsEnabled", False)

    def update_system_status(self, status_name, new_status):
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

    def report_config(self, **kwargs):
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

    def report_script_progress(self, progress):
        """Report the script progress.

        Parameters
        ----------
        progress : `int`
            Progress of the script execution (0-100%).
        """
        self.signal_script.progress.emit(int(progress))

    async def save_position(self):
        """Save the rigid body position."""
        await self.controller.write_command_to_server("saveMirrorPosition")

    async def go_to_position(self, x, y, z, rx, ry, rz):
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
            await self.controller.write_command_to_server(
                "positionMirror",
                message_details={
                    "x": x,
                    "y": y,
                    "z": z,
                    "xRot": rx,
                    "yRot": ry,
                    "zRot": rz,
                },
            )
        else:
            raise RuntimeError("Mirror can be positioned only in closed-loop control.")

    def is_enabled_and_open_loop_control(self):
        """The system is in the Enabled state and open-loop control or not.

        Returns
        -------
        `bool`
            True if the system is in the Enabled state and open-loop control.
            Otherwise, False.
        """
        return self.local_mode == LocalMode.Enable and not self.is_closed_loop

    def is_enabled_and_closed_loop_control(self):
        """The system is in the Enabled state and closed-loop control or not.

        Returns
        -------
        `bool`
            True if the system is in the Enabled state and closed-loop control.
            Otherwise, False.
        """
        return self.local_mode == LocalMode.Enable and self.is_closed_loop

    async def set_home(self):
        """Set the home position."""
        await self.controller.write_command_to_server("setMirrorHome")

    async def reboot_controller(self):
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

    def set_bit_digital_status(self, idx, value):
        """Set the bit value of digital status.

        Parameters
        ----------
        idx : `int`
            Bit index that begins from 0, which should be >= 0.
        value : `bool`
            Bit value.

        Raises
        ------
        `RuntimeError`
            Not in the diagnostic state.
        """

        if self.local_mode == LocalMode.Diagnostic:
            # TODO: Fix this in DM-36020.
            self.log.info(f"Set the {idx}th bit of digital status to be {int(value)}.")
        else:
            raise RuntimeError(
                "Bit value of digital status can only be set in the diagnostic state."
            )

    async def command_script(self, command, script_name=None):
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
        command,
        actuators=None,
        target_displacement=0,
        unit=ActuatorDisplacementUnit.Millimeter,
    ):
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

        if actuators == []:
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

    async def reset_breakers(self):
        """Reset the breakers."""

        await self.controller.write_command_to_server(
            "resetBreakers", message_details={"powerType": PowerType.Motor}
        )

        await self.controller.write_command_to_server(
            "resetBreakers", message_details={"powerType": PowerType.Communication}
        )

        self.utility_monitor.reset_breakers()

    def update_connection_information(
        self, host, port_command, port_telemetry, timeout_connection
    ):
        """Update the connection information.

        Parameters
        ----------
        host : `str`
            Host address.
        port_command : `int`
            Command port to connect.
        port_telemetry : `int`
            Telemetry port to connect.
        timeout_connection : `int` or `float`
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

    async def connect(self):
        """Connect to the M2 controller.

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
                self.update_system_status, "isCrioConnected", False
            )

        await self.controller.connect_server()

        self.update_system_status(
            "isCrioConnected", self.controller.are_clients_connected()
        )

    def _process_event(self, message=None):
        """Process the events from the M2 controller.

        Parameters
        ----------
        message : `dict` or None, optional
            Message from the M2 controller. (the default is None)
        """

        name = self._get_message_name(message)

        if name != "":

            if name == "m2AssemblyInPosition":
                self.update_system_status("isInPosition", message["inPosition"])

            elif name == "summaryState":
                summary_state = salobj.State(message["summaryState"])
                self.local_mode = self._summary_state_to_local_mode(summary_state)
                self.report_control_status()

                self.log.info(f"M2 controller has the state: {summary_state!r}.")
                self.log.info(f"Local mode is: {self.local_mode!r}.")

            elif name == "errorCode":
                error_code = message["errorCode"]
                self.add_error(error_code)

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
                self.utility_monitor.update_digital_status_output(message["value"])

            elif name == "digitalInput":
                self.utility_monitor.update_digital_status_input(message["value"])

            # Ignore these messages because they are specific to CSC
            elif name in (
                "cellTemperatureHiWarning",
                "detailedState",
                "inclinationTelemetrySource",
                "interlock",
                "tcpIpConnected",
                "temperatureOffset",
            ):
                pass

            else:
                self.log.warning(f"Unspecified event message: {name}, ignoring...")

    def _get_message_name(self, message):
        """Get the name of message.

        Parameters
        ----------
        message : `dict`
            Message.

        Returns
        -------
        `str`
            Name of the message. If there is no 'id' field, return the empty
            string.
        """

        try:
            return message["id"]
        except (TypeError, KeyError):
            return ""

    def _summary_state_to_local_mode(self, summary_state):
        """Transform the summary state to local mode.

        Parameters
        ----------
        summary_state : enum `lsst.ts.salobj.State`
            Summary state.

        Returns
        -------
        local_mode : enum `LocalMode`
            Local mode.
        """

        local_mode = LocalMode.Standby

        if summary_state == salobj.State.STANDBY:
            local_mode = LocalMode.Standby

        elif summary_state == salobj.State.DISABLED:
            local_mode = LocalMode.Diagnostic

        elif summary_state == salobj.State.ENABLED:
            local_mode = LocalMode.Enable

        # Transition to the Diagnostic state if the local mode was the Enable
        # mode originally.
        elif summary_state == salobj.State.FAULT:
            local_mode = (
                LocalMode.Diagnostic
                if self.local_mode == LocalMode.Enable
                else self.local_mode
            )

        else:
            self.log.warning(
                f"Unsupported summary state: {summary_state!r}."
                f"Use the {local_mode!r} instead."
            )

        return local_mode

    def _process_telemetry(self, message=None):
        """Process the telemetry from the M2 controller.

        Parameters
        ----------
        message : `dict` or None, optional
            Message from the M2 controller. (the default is None)
        """

        name = self._get_message_name(message)

        if name != "":

            num_axial = NUM_ACTUATOR - NUM_TANGENT_LINK

            if name == "position":
                self.utility_monitor.update_position(
                    message["x"],
                    message["y"],
                    message["z"],
                    message["xRot"],
                    message["yRot"],
                    message["zRot"],
                )

            elif name == "axialForce":
                forces = self.utility_monitor.get_forces()

                forces.f_gravity[:num_axial] = message["lutGravity"]
                forces.f_temperature[:num_axial] = message["lutTemperature"]
                forces.f_delta[:num_axial] = message["applied"]
                forces.f_cur[:num_axial] = message["measured"]
                forces.f_hc[:num_axial] = message["hardpointCorrection"]

                forces.f_error[:num_axial] = [
                    (
                        message["lutGravity"][idx]
                        + message["lutTemperature"][idx]
                        + message["applied"][idx]
                        - message["hardpointCorrection"][idx]
                        - message["measured"][idx]
                    )
                    for idx in range(num_axial)
                ]

                # Do not consider the force error in hardpoints.
                # This is the logic in M2 cell LabVIEW code by vendor. Need to
                # figure out why it was designed in this way in a latter time.
                for idx in self.utility_monitor.hard_points["axial"]:
                    # Index begins from 0 in list
                    forces.f_error[idx - 1] = 0

                self.utility_monitor.update_forces(forces)

            elif name == "tangentForce":
                forces = self.utility_monitor.get_forces()

                # There is no temperature LUT correction
                forces.f_gravity[-NUM_TANGENT_LINK:] = message["lutGravity"]
                forces.f_delta[-NUM_TANGENT_LINK:] = message["applied"]
                forces.f_cur[-NUM_TANGENT_LINK:] = message["measured"]
                forces.f_hc[-NUM_TANGENT_LINK:] = message["hardpointCorrection"]

                forces.f_error[-NUM_TANGENT_LINK:] = [
                    (
                        message["lutGravity"][idx]
                        + message["applied"][idx]
                        - message["hardpointCorrection"][idx]
                        - message["measured"][idx]
                    )
                    for idx in range(NUM_TANGENT_LINK)
                ]

                # Do not consider the force error in hardpoints.
                # This is the logic in M2 cell LabVIEW code by vendor. Need to
                # figure out why it was designed in this way in a latter time.
                for idx in self.utility_monitor.hard_points["tangent"]:
                    # Index begins from 0 in list
                    forces.f_error[idx - 1] = 0

                self.utility_monitor.update_forces(forces)

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
                    message["inclinometerProcessed"]
                )

            # If the step changes, the position will be changed as well.
            # We base on the change of position to send the "signal" to
            # update the GUI.
            elif name == "axialActuatorSteps":
                self.utility_monitor.forces.step[:num_axial] = message["steps"]

            elif name == "tangentActuatorSteps":
                self.utility_monitor.forces.step[-NUM_TANGENT_LINK:] = message["steps"]

            elif name == "axialEncoderPositions":
                forces = self.utility_monitor.get_forces()

                # The received unit is um instead of mm.
                position = message["position"]
                forces.position_in_mm[:num_axial] = [value * 1e-3 for value in position]

                self.utility_monitor.update_forces(forces)

            elif name == "tangentEncoderPositions":
                forces = self.utility_monitor.get_forces()

                # The received unit is um instead of mm.
                position = message["position"]
                forces.position_in_mm[-NUM_TANGENT_LINK:] = [
                    value * 1e-3 for value in position
                ]

                self.utility_monitor.update_forces(forces)

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

            # Ignore these messages because they are specific to CSC
            elif name in (
                "forceBalance",
                "ilcData",
                "netForcesTotal",
                "netMomentsTotal",
                "positionIMS",
            ):
                pass

            else:
                self.log.warning(f"Unspecified telemetry message: {name}, ignoring...")

    async def disconnect(self):
        """Disconnect from the M2 controller."""

        if self.controller.are_clients_connected():
            self.log.info("Disconnecting from the M2 controller...")
        else:
            self.log.info("No connection with the M2 controller.")

        await self.controller.close_tasks()
        self.update_system_status(
            "isCrioConnected", self.controller.are_clients_connected()
        )

    async def __aenter__(self):
        """This is an overridden function to support the asynchronous context
        manager."""
        return self

    async def __aexit__(self, type, value, traceback):
        """This is an overridden function to support the asynchronous context
        manager."""
        await self.controller.close_tasks()
