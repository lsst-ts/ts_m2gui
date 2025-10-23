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

__all__ = ["FaultManager"]

from lsst.ts.m2com import LimitSwitchType

from .enums import Ring, Status
from .signals import SignalError, SignalLimitSwitch


class FaultManager(object):
    """Fault manager to record the system error.

    Parameters
    ----------
    limit_switch_status : `dict`
        Default limit switch status.

    Attributes
    ----------
    signal_error : `SignalError`
        Signal to report the new or cleared errors.
    signal_limit_switch : `SignalLimitSwitch`
        Signal to report the updated status of limit switch.
    summary_faults_status : `int`
        Summary faults status in the cell controller.
    errors : `set` [`int`]
        Errors in the controller.
    limit_switch_status_retract : `dict`
        Retract limit switch status. The key is the name of limit switch. The
        value is the status in bool. True if the limit switch is triggered,
        otherwise, False.
    limit_switch_status_extend : `dict`
        Extend limit switch status. The key is the name of limit switch. The
        value is the status in bool. True if the limit switch is triggered,
        otherwise, False.
    """

    def __init__(self, limit_switch_status: dict) -> None:
        self.signal_error = SignalError()
        self.signal_limit_switch = SignalLimitSwitch()

        self.summary_faults_status = 0
        self.errors: set[int] = set()

        self.limit_switch_status_retract = limit_switch_status.copy()
        self.limit_switch_status_extend = limit_switch_status.copy()

    def update_summary_faults_status(self, status: int) -> None:
        """Update the summary faults status.

        Parameters
        ----------
        status : `int`
            New status.
        """
        if status != self.summary_faults_status:
            self.summary_faults_status = status
            self.signal_error.summary_faults_status.emit(status)

    def report_enabled_faults_mask(self, mask: int) -> None:
        """Report the enabled faults mask.

        Parameters
        ----------
        mask : `int`
            Enabled faults mask.
        """
        self.signal_error.enabled_faults_mask.emit(mask)

    def add_error(self, error: int) -> None:
        """Add the error.

        Parameters
        ----------
        error : `int`
            Error code.
        """

        if error not in self.errors:
            self.errors.add(error)
            self.signal_error.error_new.emit(error)

    def clear_error(self, error: int) -> None:
        """Clear the error.

        Parameters
        ----------
        error : `int`
            Error code.
        """

        if error in self.errors:
            self.errors.discard(error)
            self.signal_error.error_cleared.emit(error)

    def reset_errors(self) -> None:
        """Reset errors."""

        errors = list(self.errors)
        for error in errors:
            self.clear_error(error)

    def has_error(self) -> bool:
        """Has the error or not.

        Returns
        -------
        `bool`
            True if there is the error. Otherwise, False.
        """

        return len(self.errors) != 0

    def reset_limit_switch_status(self, limit_switch_type: LimitSwitchType) -> None:
        """Reset the limit switch status.

        Parameters
        ----------
        limit_switch_type : enum `lsst.ts.m2com.LimitSwitchType`
            Type of limit switch.

        Raises
        ------
        `ValueError`
            Unsupported limit switch type.
        """

        if limit_switch_type == LimitSwitchType.Retract:
            limit_switch_status = self.limit_switch_status_retract
        elif limit_switch_type == LimitSwitchType.Extend:
            limit_switch_status = self.limit_switch_status_extend
        else:
            raise ValueError(f"Unsupported limit switch type: {limit_switch_type!r}.")

        for limit_switch, status in limit_switch_status.items():
            if status != Status.Normal:
                limit_switch_status[limit_switch] = Status.Normal
                self.signal_limit_switch.type_name_status.emit(
                    (limit_switch_type, limit_switch, Status.Normal)
                )

    def update_limit_switch_status(
        self,
        limit_switch_type: LimitSwitchType,
        ring: Ring,
        number: int,
        new_status: Status,
    ) -> None:
        """Update the limit switch status.

        Parameters
        ----------
        limit_switch_type : enum `lsst.ts.m2com.LimitSwitchType`
            Type of limit switch.
        ring : enum `Ring`
            Name of ring.
        number : `int`
            Number of actuator.
        new_status : enum `Status`
            New status of limit switch.

        Raises
        ------
        `ValueError`
            Unsupported limit switch type.
        `ValueError`
            The limit switch is not in the list.
        """

        if limit_switch_type == LimitSwitchType.Retract:
            limit_switch_status = self.limit_switch_status_retract
        elif limit_switch_type == LimitSwitchType.Extend:
            limit_switch_status = self.limit_switch_status_extend
        else:
            raise ValueError(f"Unsupported limit switch type: {limit_switch_type!r}.")

        name = ring.name + str(number)
        if name in limit_switch_status.keys():
            if limit_switch_status[name] != new_status:
                limit_switch_status[name] = new_status
                self.signal_limit_switch.type_name_status.emit((limit_switch_type, name, new_status))
        else:
            raise ValueError(f"The limit switch: {name} is not in the list.")
