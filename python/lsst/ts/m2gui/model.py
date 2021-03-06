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

__all__ = ["Model"]

from . import (
    LocalMode,
    LimitSwitchType,
    Ring,
    ActuatorDisplacementUnit,
    SignalStatus,
    SignalConfig,
    SignalScript,
    FaultManager,
    Config,
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
    host : `str`
        Host address.
    port_command : `int`
        Command port to connect.
    port_telemetry : `int`
        Telemetry port to connect.
    timeout_connection : `int` or `float`
        Connection timeout in second.
    """

    def __init__(
        self,
        log,
        host="localhost",
        port_command=50010,
        port_telemetry=50011,
        timeout_connection=10,
    ):

        self.log = log

        self.is_csc_commander = False
        self.local_mode = LocalMode.Standby
        self.is_closed_loop = False

        self.signal_status = SignalStatus()
        self.signal_config = SignalConfig()
        self.signal_script = SignalScript()

        self.system_status = self._set_system_status()

        self.fault_manager = FaultManager(self.get_actuator_default_status(False))
        self.utility_monitor = UtilityMonitor()

        # TCP/IP connection information. They will be move to other places in a
        # latter time
        self.host = host
        self.port_command = port_command
        self.port_telemetry = port_telemetry
        self.timeout_connection = timeout_connection

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

    def reset_errors(self):
        """Reset errors."""

        self.log.info("Reset all errors.")

        self.fault_manager.reset_errors()
        self.fault_manager.reset_limit_switch_status(LimitSwitchType.Retract)
        self.fault_manager.reset_limit_switch_status(LimitSwitchType.Extend)

        self._check_error_and_update_status()

    def enable_open_loop_max_limit(self):
        """Enable the maximum limit in open-loop control.

        Raises
        ------
        `RuntimeError`
            Not in the open-loop control.
        """

        if self.is_enabled_and_open_loop_control():
            self.update_system_status("isOpenLoopMaxLimitsEnabled", True)
        else:
            raise RuntimeError(
                "Failed to enable the maximum limit. Only allow in Enabled state and open-loop control."
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

    def save_position(self):
        """Save the rigid body position."""
        self.log.info("Save the rigid body position.")

    def go_to_position(self, x, y, z, rx, ry, rz):
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
            self.log.info(f"Move to the position: ({x}, {y}, {z}, {rx}, {ry}, {rz}).")
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

    def set_home(self):
        """Set the home position."""
        self.log.info("Set the home position.")

    def reboot_controller(self):
        """Reboot the cell controller.

        Raises
        ------
        `RuntimeError`
            Not in the standby state with local control.
        """

        if self.local_mode == LocalMode.Standby and not self.is_csc_commander:
            self.log.info("Reboot the cell controller.")
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
            self.log.info(f"Set the {idx}th bit of digital status to be {int(value)}.")
        else:
            raise RuntimeError(
                "Bit value of digital status can only be set in the diagnostic state."
            )

    def command_script(self, command, script_name=None):
        """Run the script command.

        Parameters
        ----------
        command : enum `CommandScript`
            Script command.
        script_name : `str` or None, optional
            Name of the script. (the default is None)

        Raises
        ------
        `RuntimeError`
            Not in the enabled state.
        """

        if self.local_mode == LocalMode.Enable:
            self.log.info(f"Run the script command: {command!r}.")

            if script_name is not None:
                # Cell controller needs to check this file exists or not.
                self.log.info(f"Load the script: {script_name}.")

        else:
            raise RuntimeError(
                "Failed to run the script command. Only allowed in Enabled state."
            )

    def command_actuator(
        self,
        command,
        actuators=None,
        target_displacement=0,
        displacement_unit=ActuatorDisplacementUnit.Millimeter,
    ):
        """Run the actuator command.

        Parameters
        ----------
        command : enum `CommandActuator`
            Actuator command.
        actuators : `list [int]` or None, optional
            Selected actuators to do the movement. If the empty list [] is
            passed, the function will raise the RuntimeError. (the default is
            None)
        target_displacement : `float` or `int`, optional
            Target displacement of the actuators. (the default is 0)
        displacement_unit : enum `ActuatorDisplacementUnit`, optional
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

        if self.is_enabled_and_open_loop_control():
            self.log.info(f"Run the actuator command: {command!r}.")

            if actuators is not None:
                self.log.info(
                    (
                        f"Move {actuators} actuators with the"
                        f" displacement={target_displacement} {displacement_unit.name}."
                    )
                )
        else:
            raise RuntimeError(
                "Failed to command the actuator. Only allow in Enabled state and open-loop control."
            )

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
        """

        if self.system_status["isCrioConnected"]:
            raise RuntimeError("Please disconnect from the M2 controller first.")

        self.host = host
        self.port_command = port_command
        self.port_telemetry = port_telemetry
        self.timeout_connection = timeout_connection

    def connect(self):
        """Connect to the M2 controller.

        Raises
        ------
        `RuntimeError`
            There is the connection with the M2 controller already.
        """

        if self.system_status["isCrioConnected"]:
            raise RuntimeError("Please disconnect from the M2 controller first.")

        self.log.info("Connect to the M2 controller.")

    def disconnect(self):
        """Disconnect from the M2 controller.

        Raises
        ------
        `RuntimeError`
            There is no connection with the M2 controller yet.
        """

        if not self.system_status["isCrioConnected"]:
            raise RuntimeError("There is no connection with the M2 controller.")

        self.log.info("Disconnect from the M2 controller.")
