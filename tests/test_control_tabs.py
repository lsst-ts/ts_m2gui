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

import logging
import pytest

from PySide2 import QtCore

from lsst.ts.m2gui import ControlTabs


@pytest.fixture
def widget(qtbot):

    log = logging.getLogger()
    widget = ControlTabs(log)

    qtbot.addWidget(widget)

    return widget


def test_init(qtbot, widget):
    assert widget.count() == 9


def test_get_tab(qtbot, widget):
    tab = widget.get_tab("None")
    assert tab is None

    name = "Overview"
    tab = widget.get_tab(name)
    assert tab.text() == name


def test_flag(qtbot, widget):

    name = "Overview"
    tab = widget.get_tab(name)
    assert tab.isSelected() is False

    rect = widget.visualItemRect(tab)
    center = rect.center()
    qtbot.mouseClick(
        widget.viewport(), QtCore.Qt.LeftButton, pos=center
    )

    assert tab.isSelected() is True
