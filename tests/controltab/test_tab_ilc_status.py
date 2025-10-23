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
from pathlib import Path

import numpy as np
import pytest
import pytest_asyncio
from lsst.ts.m2com import NUM_INNER_LOOP_CONTROLLER, get_config_dir
from lsst.ts.m2gui import Model
from lsst.ts.m2gui.controltab import TabIlcStatus
from lsst.ts.xml.enums import MTM2
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot


def get_ilc_details_file() -> Path:
    return get_config_dir() / "ilc_details.yaml"


@pytest.fixture
def widget(qtbot: QtBot) -> TabIlcStatus:
    widget = TabIlcStatus("ILC Status", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest_asyncio.fixture
async def widget_async(qtbot: QtBot) -> TabIlcStatus:
    async with TabIlcStatus("ILC Status", Model(logging.getLogger(), is_simulation_mode=True)) as widget_sim:
        qtbot.addWidget(widget_sim)

        await widget_sim.model.connect()
        yield widget_sim


def test_init(widget: TabIlcStatus) -> None:
    assert len(widget._indicators_ilc) == NUM_INNER_LOOP_CONTROLLER


def test_get_indicator_color(widget: TabIlcStatus) -> None:
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Standby) == Qt.cyan
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Disabled) == Qt.blue
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Enabled) == Qt.green
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Fault) == Qt.red
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Unknown) == Qt.gray


def test_enable_ilc_commands(widget: TabIlcStatus) -> None:
    widget._enable_ilc_commands(False)
    for button in widget._buttons_ilc.values():
        assert button.isEnabled() is False

    widget._enable_ilc_commands(True)
    for button in widget._buttons_ilc.values():
        assert button.isEnabled() is True


@pytest.mark.asyncio
async def test_is_closed_loop_control_mode_in_idle(widget: TabIlcStatus) -> None:
    is_idle = await widget._is_closed_loop_control_mode_in_idle("", is_prompted=False)
    assert is_idle is True

    widget.model.controller.closed_loop_control_mode = MTM2.ClosedLoopControlMode.TelemetryOnly
    is_idle = await widget._is_closed_loop_control_mode_in_idle("", is_prompted=False)
    assert is_idle is False


@pytest.mark.asyncio
async def test_callback_ilc_state_reset(qtbot: QtBot, widget: TabIlcStatus) -> None:
    mode = MTM2.InnerLoopControlMode.Disabled
    widget.model.controller.ilc_modes[0] = mode
    widget.model._report_ilc_status(0, mode.value)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    qtbot.mouseClick(widget._buttons_ilc["reset"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert np.isnan(widget.model.controller.ilc_modes[0])

    palette = widget._indicators_ilc[1].palette()
    assert palette.color(QPalette.Button) == Qt.gray


@pytest.mark.asyncio
async def test_callback_ilc_state_check(qtbot: QtBot, widget_async: TabIlcStatus) -> None:
    controller = widget_async.model.controller
    controller.ilc_modes[:-1] = MTM2.InnerLoopControlMode.Enabled

    await controller.mock_server.model.power_communication.power_on()

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    qtbot.mouseClick(widget_async._buttons_ilc["check"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert controller.ilc_modes[-1] == MTM2.InnerLoopControlMode.Standby


@pytest.mark.asyncio
async def test_callback_ilc_state_enable(qtbot: QtBot, widget_async: TabIlcStatus) -> None:
    controller = widget_async.model.controller
    await controller.mock_server.model.power_communication.power_on()

    qtbot.mouseClick(widget_async._buttons_ilc["enable"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(5)

    assert controller.are_ilc_modes_enabled()


@pytest.mark.asyncio
async def test_callback_signal_ilc_status(qtbot: QtBot, widget: TabIlcStatus) -> None:
    mode = MTM2.InnerLoopControlMode.Disabled
    widget.model._report_ilc_status(1, mode.value)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    palette = widget._indicators_ilc[1].palette()
    color = palette.color(QPalette.Button)

    assert color == widget._get_indicator_color(mode)


@pytest.mark.asyncio
async def test_callback_signal_ilc_status_bypassed_ilcs(qtbot: QtBot, widget: TabIlcStatus) -> None:
    bypassed_ilcs = [1, 2, 3]
    widget.model.signal_ilc_status.bypassed_ilcs.emit(bypassed_ilcs)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._label_bypassed_ilcs.text() == str(bypassed_ilcs)


def test_read_ilc_details_file(widget: TabIlcStatus) -> None:
    widget.read_ilc_details_file(get_ilc_details_file())

    assert widget._indicators_ilc[0].toolTip() == "Axial actuator: B1"
    assert widget._indicators_ilc[-1].toolTip() == "Inclinometer"
