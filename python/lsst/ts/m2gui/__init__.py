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

import typing

if typing.TYPE_CHECKING:
    __version__ = "?"
else:
    try:
        from .version import *
    except ImportError:
        __version__ = "?"

from .enums import LocalMode, LimitSwitchType, Ring
from .utils import set_button
from .signals import (
    SignalControl,
    SignalMessage,
    SignalError,
    SignalStatus,
    SignalLimitSwitch,
)
from .log_window_handler import LogWindowHandler
from .fault_manager import FaultManager
from .model import Model
from .control_tabs import ControlTabs
from .main_window import MainWindow
