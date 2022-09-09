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

import asyncio
import logging

import pytest
from lsst.ts.m2gui import ControlTabs, Model
from PySide2 import QtCore
from PySide2.QtWidgets import QWidget


class MockWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout_control_tabs = ControlTabs(Model(logging.getLogger()))

        self.setLayout(self.layout_control_tabs.layout)


@pytest.fixture
def widget(qtbot):

    widget = MockWidget()
    qtbot.addWidget(widget)

    return widget


def test_init(qtbot, widget):
    assert widget.layout_control_tabs._list_widget.count() == 9


def test_get_tab(qtbot, widget):
    tab_item, control_tab = widget.layout_control_tabs.get_tab("None")
    assert tab_item is None
    assert control_tab is None

    name = "Overview"
    tab_item, control_tab = widget.layout_control_tabs.get_tab(name)
    assert tab_item.text() == name
    assert control_tab.windowTitle() == name


def test_flag_default(qtbot, widget):

    name = "Overview"
    tab_item = widget.layout_control_tabs.get_tab(name)[0]
    assert tab_item.isSelected() is True


def test_flag(qtbot, widget):

    name = "Diagnostics"
    tab_item, control_tab = widget.layout_control_tabs.get_tab(name)
    assert tab_item.isSelected() is False
    assert control_tab.isVisible() is False

    rect = widget.layout_control_tabs._list_widget.visualItemRect(tab_item)
    center = rect.center()
    qtbot.mouseClick(
        widget.layout_control_tabs._list_widget.viewport(),
        QtCore.Qt.LeftButton,
        pos=center,
    )

    assert tab_item.isSelected() is True
    assert control_tab.isVisible() is False


@pytest.mark.asyncio
async def test_show(qtbot, widget):

    names = [
        "Overview",
        "Actuator Control",
        "Configuration View",
        "Cell Status",
        "Utility View",
        "Rigid Body Position",
        "Detailed Force",
        "Diagnostics",
        "Alarms/Warnings",
    ]

    for name in names:

        tab_item, control_tab = widget.layout_control_tabs.get_tab(name)
        assert control_tab.isVisible() is False

        rect = widget.layout_control_tabs._list_widget.visualItemRect(tab_item)
        center = rect.center()

        qtbot.mousePress(
            widget.layout_control_tabs._list_widget.viewport(),
            QtCore.Qt.LeftButton,
            pos=center,
        )

        qtbot.mouseDClick(
            widget.layout_control_tabs._list_widget.viewport(),
            QtCore.Qt.LeftButton,
            pos=center,
        )

        # Sleep so the event loop can access CPU to handle the signal
        await asyncio.sleep(1)

        assert tab_item.isSelected() is True
        assert control_tab.isVisible() is True
