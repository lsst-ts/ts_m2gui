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

import asyncio

import pytest
from lsst.ts.m2gui import MainWindow
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QToolBar


@pytest.fixture
def widget(qtbot):

    widget = MainWindow(False, False, log_level=13)
    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def widget_sim(qtbot):

    widget_sim = MainWindow(False, True)
    qtbot.addWidget(widget_sim)

    return widget_sim


def test_init(widget):

    assert widget.log.level == 13

    tool_bar = widget.findChildren(QToolBar)[0]
    actions = tool_bar.actions()

    assert len(actions) == 4

    assert widget.model.host == "m2-crio-controller01.cp.lsst.org"
    assert widget.model.port_command == 50010
    assert widget.model.port_telemetry == 50011
    assert widget.model.timeout_connection == 10


def test_init_sim(widget_sim):

    assert widget_sim.model.host == "127.0.0.1"


def test_get_action(widget):

    button_exit = widget._get_action("Exit")
    assert button_exit.text() == "Exit"

    button_wrong_action = widget._get_action("WrongAction")
    assert button_wrong_action is None


async def test_callback_settings(qtbot, widget):

    assert widget._tab_settings.isVisible() is False

    button_settings = widget._get_action("Settings")
    qtbot.mouseClick(button_settings, Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tab_settings.isVisible() is True
