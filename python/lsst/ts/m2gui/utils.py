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

__all__ = ["set_button", "get_rgb_from_hex", "colors"]

from functools import partial
from PySide2.QtWidgets import QPushButton
from PySide2.QtGui import QColor

colors = {
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "Black": "#000000",
    "White": "#FFFFFF",
    "Electric Green": "#41CD52",
    "Dark Blue": "#222840",
    "Yellow": "#F9E56d",
}


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


def get_rgb_from_hex(code):
    """Get RGB color from hexadecimal code.

    Parameters
    ----------
    code : `str`
        Hexadecimal code.

    Returns
    -------
    `PySide2.QtGui.QColor`
        Color.
    """

    code_hex = code.replace("#", "")
    rgb = tuple(int(code_hex[idx : idx + 2], 16) for idx in (0, 2, 4))

    return QColor.fromRgb(rgb[0], rgb[1], rgb[2])
