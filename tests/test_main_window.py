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

import pytest

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QToolBar

from lsst.ts.m2gui import MainWindow


def get_button_action(tool_bar, name):

    actions = tool_bar.actions()
    for action in actions:
        if action.text() == name:
            return tool_bar.widgetForAction(action)

    return None


@pytest.fixture
def widget(qtbot):

    widget = MainWindow(False)
    qtbot.addWidget(widget)

    return widget


def test_init(widget):

    tool_bar = widget.findChildren(QToolBar)[0]
    actions = tool_bar.actions()

    assert len(actions) == 4

    assert widget.model.host == "m2-crio-controller01.cp.lsst.org"
    assert widget.model.port_command == 50010
    assert widget.model.port_telemetry == 50011
    assert widget.model.timeout_connection == 10


def test_callback_settings(qtbot, widget):

    assert widget._tab_settings.isVisible() is False

    tool_bar = widget.findChildren(QToolBar)[0]
    button_settings = get_button_action(tool_bar, "Settings")

    qtbot.mouseClick(button_settings, Qt.LeftButton)

    assert widget._tab_settings.isVisible() is True
