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

__all__ = ["set_button", "LocalMode"]

from enum import IntEnum, auto
from functools import partial
from PySide2.QtWidgets import QPushButton


class LocalMode(IntEnum):
    Standby = 1
    Diagnostic = auto()
    Enable = auto()


def set_button(name, callback, *args, is_checkable=False):
    """Set the button.

    Parameters
    ----------
    name : `str`
        Button name.
    callback : `func`
        Callback function object to use in future partial calls.
    *args : `args`
        Tuple of callback arguments to future partial calls.
    is_checkable : `bool`, optional
        The button is checkable or not. (the default is False)

    Returns
    -------
    button : `PySide2.QtWidgets.QPushButton`
        button.
    """

    button = QPushButton(name)
    if is_checkable:
        button.setCheckable(is_checkable)

    button.clicked.connect(partial(callback, *args))

    return button
