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

import pytest
import pytest_asyncio
from lsst.ts.m2com import NUM_ACTUATOR, get_config_dir
from lsst.ts.m2gui import LocalMode, Model
from lsst.ts.m2gui.controltab import TabHardpointSelection
from PySide2.QtCore import Qt
from pytestqt.qtbot import QtBot


def get_cell_geometry_file() -> Path:
    return get_config_dir() / "harrisLUT" / "cell_geom.yaml"


@pytest.fixture
def widget(qtbot: QtBot) -> TabHardpointSelection:
    widget = TabHardpointSelection("Hardpoints", Model(logging.getLogger()))
    widget.read_cell_geometry_file(get_cell_geometry_file())
    qtbot.addWidget(widget)

    return widget


@pytest_asyncio.fixture
async def widget_async(qtbot: QtBot) -> TabHardpointSelection:
    async with TabHardpointSelection(
        "Hardpoints", Model(logging.getLogger(), is_simulation_mode=True)
    ) as widget_sim:
        widget_sim.read_cell_geometry_file(get_cell_geometry_file())
        qtbot.addWidget(widget_sim)

        await widget_sim.model.connect()
        yield widget_sim


def test_init(widget: TabHardpointSelection) -> None:
    assert len(widget._cell_geom.keys()) == 3


@pytest.mark.asyncio
async def test_callback_reset_default_no_hardpoints(
    qtbot: QtBot, widget: TabHardpointSelection
) -> None:
    # Select an actuator
    idx = 2
    widget._buttons_hardpoint_selection[idx].setChecked(True)

    qtbot.mouseClick(widget._buttons_hardpoint["reset"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._buttons_hardpoint_selection[idx].isChecked() is False


@pytest.mark.asyncio
async def test_callback_reset_default_with_hardpoints(
    qtbot: QtBot, widget: TabHardpointSelection
) -> None:
    widget._hardpoints = [1, 2, 3]

    qtbot.mouseClick(widget._buttons_hardpoint["reset"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for idx in range(NUM_ACTUATOR):
        if idx in widget._hardpoints:
            assert widget._buttons_hardpoint_selection[idx].isChecked() is True
        else:
            assert widget._buttons_hardpoint_selection[idx].isChecked() is False


@pytest.mark.asyncio
async def test_suggest_hardpoints_error(widget: TabHardpointSelection) -> None:
    # No selection
    with pytest.raises(ValueError):
        widget._suggest_hardpoints()

    # No selection of tangent link
    widget._buttons_hardpoint_selection[0].setChecked(True)

    with pytest.raises(ValueError):
        widget._suggest_hardpoints()


@pytest.mark.asyncio
async def test_callback_suggest_hardpoints(
    qtbot: QtBot, widget: TabHardpointSelection
) -> None:
    for idx in (0, 72):
        widget._buttons_hardpoint_selection[idx].setChecked(True)

    qtbot.mouseClick(widget._buttons_hardpoint["suggest"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for idx in range(NUM_ACTUATOR):
        if idx in (0, 10, 20, 72, 74, 76):
            assert widget._buttons_hardpoint_selection[idx].isChecked() is True
        else:
            assert widget._buttons_hardpoint_selection[idx].isChecked() is False


@pytest.mark.asyncio
async def test_set_hardpoint_list_error(widget: TabHardpointSelection) -> None:
    # No selection
    with pytest.raises(ValueError):
        await widget._set_hardpoint_list()

    # Not in the Standby state
    for idx in (5, 15, 25, 73, 75, 77):
        widget._buttons_hardpoint_selection[idx].setChecked(True)

    widget.model.local_mode = LocalMode.Diagnostic
    with pytest.raises(RuntimeError):
        await widget._set_hardpoint_list()


@pytest.mark.asyncio
async def test_callback_apply_hardpoints(
    qtbot: QtBot, widget_async: TabHardpointSelection
) -> None:

    assert widget_async._hardpoints == [5, 15, 25, 73, 75, 77]

    hardpoints = [2, 12, 22, 72, 74, 76]
    for idx in range(NUM_ACTUATOR):
        if idx in hardpoints:
            widget_async._buttons_hardpoint_selection[idx].setChecked(True)
        else:
            widget_async._buttons_hardpoint_selection[idx].setChecked(False)

    qtbot.mouseClick(widget_async._buttons_hardpoint["apply"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(2)

    await widget_async.model.enter_diagnostic()

    assert widget_async._hardpoints == hardpoints
