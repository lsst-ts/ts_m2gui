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

__all__ = [
    "set_button",
    "create_label",
    "create_group_box",
    "create_table",
    "get_tol",
    "get_num_actuator_ring",
    "prompt_dialog_warning",
    "run_command",
    "get_button_action",
]

import asyncio
from functools import partial

from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QGroupBox, QLabel, QPushButton, QTableWidget

from . import Ring
from .widget import QMessageBoxAsync


def set_button(
    name,
    callback,
    *args,
    is_checkable=False,
    is_indicator=False,
    is_adjust_size=False,
    tool_tip=None,
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
    tool_tip : `str` or None, optional
        Tool tip. If None, there will be no tip. (the default is None)

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

    if tool_tip is not None:
        button.setToolTip(tool_tip)

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


def create_table(header_text, is_disabled_selection=False):
    """Create the table.

    Parameters
    ----------
    header_text : `list`
        Text of the header.
    is_disabled_selection : `bool`, optional
        The selection is disabled or not. (the default is False)

    Returns
    -------
    table : `PySide2.QtWidgets.QTableWidget`
        Table.
    """

    table = QTableWidget()

    table.setColumnCount(len(header_text))
    table.setHorizontalHeaderLabels(header_text)

    if is_disabled_selection:
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setFocusPolicy(Qt.NoFocus)
        table.setSelectionMode(QTableWidget.NoSelection)

    return table


def get_tol(num_digit_after_decimal):
    """Get the tolerance.

    Parameters
    ----------
    num_digit_after_decimal : `int`
        Number of digits after the decimal. This should be greater than 0.

    Returns
    -------
    `float`
        Tolerance.
    """

    return 10 ** -int(num_digit_after_decimal)


def get_num_actuator_ring(ring):
    """Get the number of actuators on the specific ring.

    Parameters
    ----------
    ring : enum `Ring`
        Specific ring.

    Returns
    -------
    `int`
        Number of the actuators.

    Raises
    ------
    `ValueError`
        Not supported ring.
    """

    if ring == Ring.A:
        return 6
    elif ring == Ring.B:
        return 30
    elif ring == Ring.C:
        return 24
    elif ring == Ring.D:
        return 18
    else:
        raise ValueError(f"Not supported ring: {ring!r}")


async def prompt_dialog_warning(title, description, is_prompted=True):
    """Shows a warning dialog.

    The user must react to this dialog. The rest of the GUI is blocked until
    the dialog is dismissed.

    Parameters
    ----------
    title : `str`
        Title of the dialog.
    description : `str`
        Description message to be shown in the dialog.
    is_prompted : `bool`, optional
        When False, dialog will not be executed. That is used for tests, which
        shall not be the case when used in the real GUI. (the default is True)
    """

    dialog = QMessageBoxAsync()
    dialog.setIcon(QMessageBoxAsync.Warning)
    dialog.setWindowTitle(title)
    dialog.setText(description)

    # Block the user to interact with other running widgets
    dialog.setModal(True)

    if is_prompted:
        await dialog.show()


async def run_command(command, *args, is_prompted=True):
    """Run the command. This command can be a normal function or coroutine.

    If the command fails, there will be a prompt dialog to warn the users
    by default.

    Parameters
    ----------
    command : `func` or `coroutine`
        Command to execute.
    *args : `args`
        Arguments of the command.
    is_prompted : `bool`, optional
        When False, dialog will not be executed. That is used for tests, which
        shall not be the case when used in the real GUI. (the default is True)

    Returns
    -------
    `bool`
        True if the command succeeds. Otherwise, False.
    """

    is_coroutine = asyncio.iscoroutine(command) or asyncio.iscoroutinefunction(command)
    try:
        if is_coroutine:
            await command(*args)
        else:
            command(*args)
    except Exception as error:
        await prompt_dialog_warning(
            f"{command.__name__}()", str(error), is_prompted=is_prompted
        )

        return False

    return True


def get_button_action(tool_bar, name):
    """Get the button widget of action in tool bar.

    Parameters
    ----------
    tool_bar : `PySide2.QtWidgets.QToolBar`
        Tool bar.
    name : `str`
        Action name.

    Returns
    -------
    `PySide2.QtWidgets.QAction` or None
        Button widget of the action. None if does not exist.
    """

    actions = tool_bar.actions()
    for action in actions:
        if action.text() == name:
            return tool_bar.widgetForAction(action)

    return None
