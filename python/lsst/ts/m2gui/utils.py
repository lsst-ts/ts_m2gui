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

__all__ = ["set_button", "create_label", "create_group_box"]

from functools import partial

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPushButton, QLabel, QGroupBox
from PySide2.QtGui import QPalette


def set_button(
    name, callback, *args, is_checkable=False, is_indicator=False, is_adjust_size=False
):
    """Set the button.

    Parameters
    ----------
    name : `str`
        Button name.
    callback : `func` or None
        Callback function object to use in future partial calls. Put None
        if you do not want to have the callback function connected.
    *args : `args`
        Tuple of callback arguments to future partial calls. This is only
        meaningful if the callback is not None.
    is_checkable : `bool`, optional
        The button is checkable or not. (the default is False)
    is_indicator : `bool`, optional
        The button is indicator or not. Put the callback to be None if the
        value is True. (the default is False)
    is_adjust_size : `bool`, optional
        Adjust the size of button or not. (the default is False)

    Returns
    -------
    button : `PySide2.QtWidgets.QPushButton`
        button.
    """

    button = QPushButton(name)
    if is_checkable:
        button.setCheckable(is_checkable)

    if callback is not None:
        button.clicked.connect(partial(callback, *args))

    if is_indicator:
        button.setEnabled(False)
        button.setAutoFillBackground(True)

        palette = button.palette()
        palette.setColor(QPalette.ButtonText, Qt.black)

        button.setPalette(palette)

    if is_adjust_size:
        button.adjustSize()

    return button


def create_label(name="", point_size=None, is_bold=False):
    """Create the label.

    Parameters
    ----------
    name : `str`, optional
        Label name. (the default is "")
    point_size : `int` or None, optional
        Point size of label. The value should be greater than 0. Put None if
        use the system default. (the default is None)
    is_bold : `bool`
        Is the bold format or not. (the default is False)

    Returns
    -------
    label : `PySide2.QtWidgets.QLabel`
        label.
    """
    label = QLabel(name)

    # Set the specific font
    font = label.font()

    if point_size is not None:
        font.setPointSize(point_size)

    if is_bold:
        font.setBold(True)

    label.setFont(font)

    return label


def create_group_box(name, layout):
    """Create the group box.

    Parameters
    ----------
    name : `str`
        Name of the group box.
    layout : Layout in `PySide2.QtWidgets`
        Layout.

    Returns
    -------
    group_box : `PySide2.QtWidgets.QGroupBox`
        Group box.
    """

    group_box = QGroupBox(name)
    group_box.setLayout(layout)

    return group_box
