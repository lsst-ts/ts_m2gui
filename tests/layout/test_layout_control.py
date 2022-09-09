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
import pytest_asyncio
from lsst.ts.m2gui import LocalMode, Model, is_jenkins
from lsst.ts.m2gui.controltab import TabDefault
from lsst.ts.m2gui.layout import LayoutControl
from PySide2 import QtCore


class MockWidget(TabDefault):
    def __init__(self, title, model):
        super().__init__(title, model)

        self.layout_control = LayoutControl(self.model)

        self.widget().setLayout(self.layout_control.layout)


@pytest.fixture
def widget(qtbot):

    widget = MockWidget("Mock", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest_asyncio.fixture
async def widget_async(qtbot):
    async with MockWidget(
        "Mock", Model(logging.getLogger(), is_simulation_mode=True)
    ) as widget_sim:
        qtbot.addWidget(widget_sim)

        await widget_sim.model.connect()
        yield widget_sim


@pytest.mark.asyncio
async def test_callback_signal_control_normal(qtbot, widget):
    widget.layout_control.model.report_control_status()

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.layout_control._button_remote.isEnabled() is True
    assert widget.layout_control._button_local.isEnabled() is False


@pytest.mark.asyncio
async def test_callback_signal_control_prohibit_control(qtbot, widget):
    widget.layout_control.model.local_mode = LocalMode.Diagnostic

    widget.layout_control.model.report_control_status()

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.layout_control._button_remote.isEnabled() is False
    assert widget.layout_control._button_local.isEnabled() is False


@pytest.mark.skipif(
    is_jenkins(), reason="Jenkins failed to initiate the context manager."
)
@pytest.mark.asyncio
async def test_set_csc_commander(qtbot, widget_async):

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget_async.model.is_csc_commander is True
    assert widget_async.layout_control._button_remote.isEnabled() is False
    assert widget_async.layout_control._button_local.isEnabled() is True

    qtbot.mouseClick(widget_async.layout_control._button_local, QtCore.Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget_async.model.is_csc_commander is False
    assert widget_async.layout_control._button_remote.isEnabled() is True
    assert widget_async.layout_control._button_local.isEnabled() is False

    qtbot.mouseClick(widget_async.layout_control._button_remote, QtCore.Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget_async.model.is_csc_commander is True
    assert widget_async.layout_control._button_remote.isEnabled() is False
    assert widget_async.layout_control._button_local.isEnabled() is True
