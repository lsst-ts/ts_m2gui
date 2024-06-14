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
import typing

import pytest
import pytest_asyncio
from lsst.ts.m2gui import LocalMode, Model
from lsst.ts.m2gui.controltab import TabDefault
from lsst.ts.m2gui.layout import LayoutLocalMode
from PySide6 import QtCore
from pytestqt.qtbot import QtBot


class MockWidget(TabDefault):
    def __init__(self, title: str, model: Model) -> None:
        super().__init__(title, model)

        self.layout_local_mode = LayoutLocalMode(self.model)

        self.widget().setLayout(self.layout_local_mode.layout)


@pytest.fixture
def widget(qtbot: QtBot) -> MockWidget:
    widget = MockWidget("Mock", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest_asyncio.fixture
async def widget_async(qtbot: QtBot) -> typing.AsyncGenerator:
    async with MockWidget(
        "Mock", Model(logging.getLogger(), is_simulation_mode=True)
    ) as widget_sim:
        qtbot.addWidget(widget_sim)

        await widget_sim.model.connect()
        yield widget_sim


# Need to add this to make the above widget_async() to work on Jenkins.
# I guess there is some bug in "pytest" and "pytest_asyncio" libraries.
def test_init(widget: MockWidget) -> None:
    pass


@pytest.mark.asyncio
async def test_callback_signal_control_normal(qtbot: QtBot, widget: MockWidget) -> None:
    widget.layout_local_mode.model.report_control_status()

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.layout_local_mode._button_standby.isEnabled() is False
    assert widget.layout_local_mode._button_diagnostic.isEnabled() is True
    assert widget.layout_local_mode._button_enable.isEnabled() is False


@pytest.mark.asyncio
async def test_callback_signal_control_prohibit_control(
    qtbot: QtBot, widget: MockWidget
) -> None:
    # CSC has the control
    widget.layout_local_mode.model.is_csc_commander = True

    widget.layout_local_mode.model.report_control_status()

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    _assert_prohibit_transition(widget)

    # System is in the closed-loop control
    widget.layout_local_mode.model.is_csc_commander = False
    widget.layout_local_mode.model.is_closed_loop = True

    widget.layout_local_mode.model.report_control_status()

    _assert_prohibit_transition(widget)


def _assert_prohibit_transition(widget: MockWidget) -> None:
    assert widget.layout_local_mode._button_standby.isEnabled() is False
    assert widget.layout_local_mode._button_diagnostic.isEnabled() is False
    assert widget.layout_local_mode._button_enable.isEnabled() is False


@pytest.mark.asyncio
async def test_set_local_mode(qtbot: QtBot, widget_async: MockWidget) -> None:
    controller = widget_async.model.controller
    await controller.switch_command_source(False)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget_async.layout_local_mode._button_standby.isEnabled() is False
    assert widget_async.layout_local_mode._button_diagnostic.isEnabled() is True
    assert widget_async.layout_local_mode._button_enable.isEnabled() is False

    qtbot.mouseClick(
        widget_async.layout_local_mode._button_diagnostic, QtCore.Qt.LeftButton
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(15)

    assert widget_async.model.local_mode == LocalMode.Diagnostic

    assert widget_async.layout_local_mode._button_standby.isEnabled() is True
    assert widget_async.layout_local_mode._button_diagnostic.isEnabled() is False
    assert widget_async.layout_local_mode._button_enable.isEnabled() is True

    qtbot.mouseClick(
        widget_async.layout_local_mode._button_enable, QtCore.Qt.LeftButton
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(20)

    assert widget_async.model.local_mode == LocalMode.Enable

    assert widget_async.layout_local_mode._button_standby.isEnabled() is False
    assert widget_async.layout_local_mode._button_diagnostic.isEnabled() is True
    assert widget_async.layout_local_mode._button_enable.isEnabled() is False

    await widget_async.model.controller.enable_open_loop_max_limit(True)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(5)

    assert widget_async.model.system_status["isOpenLoopMaxLimitsEnabled"] is True

    qtbot.mouseClick(
        widget_async.layout_local_mode._button_diagnostic, QtCore.Qt.LeftButton
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(5)

    qtbot.mouseClick(
        widget_async.layout_local_mode._button_standby, QtCore.Qt.LeftButton
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(5)

    assert widget_async.model.local_mode == LocalMode.Standby

    assert widget_async.layout_local_mode._button_standby.isEnabled() is False
    assert widget_async.layout_local_mode._button_diagnostic.isEnabled() is True
    assert widget_async.layout_local_mode._button_enable.isEnabled() is False

    assert widget_async.model.system_status["isOpenLoopMaxLimitsEnabled"] is True
