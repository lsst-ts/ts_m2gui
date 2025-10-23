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
from lsst.ts.guitool import get_tol
from lsst.ts.m2gui import Model
from lsst.ts.m2gui.controltab import TabRigidBodyPos
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabRigidBodyPos:
    widget = TabRigidBodyPos("Rigid Body Position", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabRigidBodyPos) -> None:
    num_digit_after_decimal = widget.model.utility_monitor.NUM_DIGIT_AFTER_DECIMAL
    assert widget._target_position_relative["x"].decimals() == num_digit_after_decimal

    assert widget._target_position_relative["y"].singleStep() == get_tol(num_digit_after_decimal)

    assert widget._target_position_relative["z"].maximum() == widget.MAX_DISTANCE_IN_UM
    assert widget._target_position_relative["z"].minimum() == -widget.MAX_DISTANCE_IN_UM

    assert widget._target_position_relative["rx"].maximum() == widget.MAX_ROTATION_IN_ARCSEC
    assert widget._target_position_relative["ry"].minimum() == -widget.MAX_ROTATION_IN_ARCSEC


@pytest.mark.asyncio
async def test_callback_clear_values_relative(qtbot: QtBot, widget: TabRigidBodyPos) -> None:
    for idx, axis in enumerate(widget.AXES):
        widget._target_position_relative[axis].setValue(idx)

    qtbot.mouseClick(widget._buttons["clear_values_relative"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for position in widget._target_position_relative.values():
        assert position.value() == 0


@pytest.mark.asyncio
async def test_callback_clear_values_absolute(qtbot: QtBot, widget: TabRigidBodyPos) -> None:
    for idx, axis in enumerate(widget.AXES):
        widget._target_position_absolute[axis].setValue(idx)

    qtbot.mouseClick(widget._buttons["clear_values_absolute"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for position in widget._target_position_absolute.values():
        assert position.value() == 0


@pytest.mark.asyncio
async def test_callback_position(widget: TabRigidBodyPos) -> None:
    widget.model.utility_monitor.update_position(1, 2, 3, 4, 5, 6, is_ims=False)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for idx, axis in enumerate(widget.AXES):
        assert widget._position[axis].text() == str(idx + 1)


@pytest.mark.asyncio
async def test_callback_position_ims(widget: TabRigidBodyPos) -> None:
    widget.model.utility_monitor.update_position(1, 2, 3, 4, 5, 6, is_ims=True)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for idx, axis in enumerate(widget.AXES):
        assert widget._position_ims[axis].text() == str(idx + 1)
