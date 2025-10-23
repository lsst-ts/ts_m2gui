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
from lsst.ts.m2com import LimitSwitchType
from lsst.ts.m2gui import Model, Ring, Status
from lsst.ts.m2gui.controltab import TabLimitSwitchStatus
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot

SLEEP_TIME_SHORT = 1


@pytest.fixture
def widget(qtbot: QtBot) -> TabLimitSwitchStatus:
    widget = TabLimitSwitchStatus("Limit Switch Status", Model(logging.getLogger()))

    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabLimitSwitchStatus) -> None:
    for limit_switch_status in (
        widget._indicators_limit_switch_retract,
        widget._indicators_limit_switch_extend,
    ):
        for indicator in limit_switch_status.values():
            assert indicator.isEnabled() is False
            assert indicator.autoFillBackground() is True

            palette = indicator.palette()
            color = palette.color(QPalette.Button)

            assert color == Qt.green


@pytest.mark.asyncio
async def test_callback_signal_limit_switch_alert(qtbot: QtBot, widget: TabLimitSwitchStatus) -> None:
    widget.model.fault_manager.update_limit_switch_status(LimitSwitchType.Extend, Ring.B, 2, Status.Alert)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    indicator = widget._indicators_limit_switch_extend["B2"]
    palette = indicator.palette()
    color = palette.color(QPalette.Button)

    assert color == Qt.yellow


@pytest.mark.asyncio
async def test_callback_signal_limit_switch_error(qtbot: QtBot, widget: TabLimitSwitchStatus) -> None:
    widget.model.fault_manager.update_limit_switch_status(LimitSwitchType.Extend, Ring.C, 3, Status.Error)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    indicator = widget._indicators_limit_switch_extend["C3"]
    palette = indicator.palette()
    color = palette.color(QPalette.Button)

    assert color == Qt.red
