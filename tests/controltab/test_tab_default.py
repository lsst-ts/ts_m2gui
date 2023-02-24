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

import logging

import pytest
from lsst.ts.m2gui import Model
from lsst.ts.m2gui.controltab import TabDefault
from PySide2.QtWidgets import QScrollArea, QWidget


@pytest.fixture
def widget(qtbot):
    widget = TabDefault("Default", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget):
    assert widget.windowTitle() == "Default"


def test_set_widget_scrollable(widget):
    scroll_area = widget.set_widget_scrollable(QWidget())
    assert type(scroll_area) is QScrollArea

    scroll_area_resizable = widget.set_widget_scrollable(QWidget(), is_resizable=True)
    assert scroll_area_resizable.widgetResizable() is True


def test_create_and_start_timer(widget):
    timer = widget.create_and_start_timer(None)

    assert timer.interval() == widget.model.duration_refresh
    assert timer.isActive() is True


def test_check_duration_and_restart_timer(widget):
    timer = widget.create_and_start_timer(None)

    widget.model.duration_refresh = 1000
    widget.check_duration_and_restart_timer(timer)

    assert timer.interval() == widget.model.duration_refresh
    assert timer.isActive() is True
