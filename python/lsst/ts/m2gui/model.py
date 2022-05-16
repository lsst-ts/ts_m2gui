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
    SignalStatus,
    SignalConfig,
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
    system_status : `dict`
        System status.
    fault_manager : `FaultManager`
        Fault manager to record the system error.
    utility_monitor : `UtilityMonitor`
        Utility monitor to monitor the utility status.
    """

    def __init__(self, log):

        self.log = log

        self.is_csc_commander = False
        self.local_mode = LocalMode.Standby
        self.is_closed_loop = False

        self.signal_status = SignalStatus()
        self.signal_config = SignalConfig()

        self.system_status = self._set_system_status()

        self.fault_manager = FaultManager(self.get_actuator_default_status(False))
        self.utility_monitor = UtilityMonitor()

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
        """Enable the maximum limit in open-loop control."""

        if (self.local_mode == LocalMode.Enable) and not self.is_closed_loop:
            self.update_system_status("isOpenLoopMaxLimitsEnabled", True)
        else:
            self.log.info(
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
        ValueError
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
        KeyError
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

    def save_position(self):
        """Save the rigid body position."""
        self.log.info("Save the rigid body position.")

    def go_to_position(self, x, y, z, rx, ry, rz):
        """Go to the position.

        Parameters
        ----------
        x : `float`
            Position x in mm.
        y : `float`
            Position y in mm.
        z : `float`
            Position z in mm.
        rx : `float`
            Rotation x in urad.
        ry : `float`
            Rotation y in urad.
        rz : `float`
            Rotation z in urad.
        """

        if self.is_enabled_and_closed_loop_control():
            self.log.info(f"Move to the position: ({x}, {y}, {z}, {rx}, {ry}, {rz}).")
        else:
            self.log.info("This can only be done in the closed-loop control.")

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
