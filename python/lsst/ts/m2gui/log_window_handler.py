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

__all__ = ["LogWindowHandler"]

import logging

from . import SignalMessage


class LogWindowHandler(logging.Handler):
    """Log window handler.

    Parameters
    ----------
    signal_message : `SignalMessage`
        Signal of the new message.
    message_format : `str`
        Format of the message.
    """

    def __init__(self, signal_message: SignalMessage, message_format: str) -> None:
        super().__init__()

        self._signal_message = signal_message
        self._formatter = logging.Formatter(message_format)

    def emit(self, record: logging.LogRecord) -> None:
        self._signal_message.message.emit(self._formatter.format(record))
