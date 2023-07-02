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
from lsst.ts.m2gui import Model
from lsst.ts.m2gui.controltab import TabNetForceMoment
from PySide2.QtCore import Qt
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabNetForceMoment:
    widget = TabNetForceMoment("Net Force/Moment", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_callback_button_realtime_net_force_moment_total(
    qtbot: QtBot, widget: TabNetForceMoment
) -> None:
    assert widget._tab_realtime_net_force_moment_total.isVisible() is False

    qtbot.mouseClick(widget._button_realtime_net_force_moment_total, Qt.LeftButton)

    assert widget._tab_realtime_net_force_moment_total.isVisible() is True


@pytest.mark.asyncio
async def test_callback_button_realtime_force_balance(
    qtbot: QtBot, widget: TabNetForceMoment
) -> None:
    assert widget._tab_realtime_force_balance.isVisible() is False

    qtbot.mouseClick(widget._button_realtime_force_balance, Qt.LeftButton)

    assert widget._tab_realtime_force_balance.isVisible() is True


@pytest.mark.asyncio
async def test_callback_signal_net_force_total(widget: TabNetForceMoment) -> None:
    widget.model.utility_monitor.update_net_force_moment_total(
        [1.11, -2.22, 3.56], is_force=True
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tab_realtime_net_force_moment_total.net_force_moment[0:3] == [
        1.1,
        -2.2,
        3.6,
    ]

    assert widget._net_force_moment_total["fx"].text() == "1.1 N"
    assert widget._net_force_moment_total["fy"].text() == "-2.2 N"
    assert widget._net_force_moment_total["fz"].text() == "3.6 N"


@pytest.mark.asyncio
async def test_callback_signal_net_moment_total(widget: TabNetForceMoment) -> None:
    widget.model.utility_monitor.update_net_force_moment_total(
        [1.11, -2.22, 3.56], is_force=False
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tab_realtime_net_force_moment_total.net_force_moment[-3:] == [
        1.1,
        -2.2,
        3.6,
    ]

    assert widget._net_force_moment_total["mx"].text() == "1.1 N m"
    assert widget._net_force_moment_total["my"].text() == "-2.2 N m"
    assert widget._net_force_moment_total["mz"].text() == "3.6 N m"


@pytest.mark.asyncio
async def test_callback_signal_force_balance(widget: TabNetForceMoment) -> None:
    widget.model.utility_monitor.update_force_balance(
        [1.11, -2.22, 3.56, 4.41, -5.41, -6.78]
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tab_realtime_force_balance.net_force_moment == [
        1.1,
        -2.2,
        3.6,
        4.4,
        -5.4,
        -6.8,
    ]

    assert widget._force_balance["fx"].text() == "1.1 N"
    assert widget._force_balance["fy"].text() == "-2.2 N"
    assert widget._force_balance["fz"].text() == "3.6 N"
    assert widget._force_balance["mx"].text() == "4.4 N m"
    assert widget._force_balance["my"].text() == "-5.4 N m"
    assert widget._force_balance["mz"].text() == "-6.8 N m"
