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
import asyncio
import logging

from PySide2 import QtCore
from PySide2.QtWidgets import QWidget

from lsst.ts.m2gui import Model, LocalMode
from lsst.ts.m2gui.layout import LayoutControlMode


class MockWidget(QWidget):
    def __init__(self):
        super().__init__()

        model = Model(logging.getLogger())
        self.layout_control_mode = LayoutControlMode(model)

        self.setLayout(self.layout_control_mode.layout)


@pytest.fixture
def widget(qtbot):

    widget = MockWidget()
    qtbot.addWidget(widget)

    return widget


async def test_callback_signal_control_normal(qtbot, widget):
    widget.layout_control_mode.model.report_control_status()

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.layout_control_mode._button_open_loop.isEnabled() is False
    assert widget.layout_control_mode._button_closed_loop.isEnabled() is False


async def test_callback_signal_control_prohibit_control(qtbot, widget):
    widget.layout_control_mode.model.local_mode = LocalMode.Enable

    widget.layout_control_mode.model.report_control_status()

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.layout_control_mode._button_open_loop.isEnabled() is False
    assert widget.layout_control_mode._button_closed_loop.isEnabled() is True


async def test_switch_force_balance_system(qtbot, widget):
    widget.layout_control_mode.model.local_mode = LocalMode.Enable

    widget.layout_control_mode.switch_force_balance_system(True)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.layout_control_mode.model.is_closed_loop is True
    assert widget.layout_control_mode._button_open_loop.isEnabled() is True
    assert widget.layout_control_mode._button_closed_loop.isEnabled() is False

    qtbot.mouseClick(widget.layout_control_mode._button_open_loop, QtCore.Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.layout_control_mode.model.is_closed_loop is False
    assert widget.layout_control_mode._button_open_loop.isEnabled() is False
    assert widget.layout_control_mode._button_closed_loop.isEnabled() is True

    widget.layout_control_mode.model.enable_open_loop_max_limit()
    assert (
        widget.layout_control_mode.model.system_status["isOpenLoopMaxLimitsEnabled"]
        is True
    )

    qtbot.mouseClick(
        widget.layout_control_mode._button_closed_loop, QtCore.Qt.LeftButton
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.layout_control_mode.model.is_closed_loop is True
    assert widget.layout_control_mode._button_open_loop.isEnabled() is True
    assert widget.layout_control_mode._button_closed_loop.isEnabled() is False

    assert (
        widget.layout_control_mode.model.system_status["isOpenLoopMaxLimitsEnabled"]
        is False
    )
