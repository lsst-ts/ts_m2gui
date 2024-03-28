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
from lsst.ts.m2com import NUM_INNER_LOOP_CONTROLLER, get_config_dir
from lsst.ts.m2gui import Model
from lsst.ts.m2gui.controltab import TabIlcStatus
from lsst.ts.xml.enums import MTM2
from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette
from pytestqt.qtbot import QtBot


def get_ilc_details_file() -> Path:
    return get_config_dir() / "ilc_details.yaml"


@pytest.fixture
def widget(qtbot: QtBot) -> TabIlcStatus:
    widget = TabIlcStatus("ILC Status", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabIlcStatus) -> None:
    assert len(widget._indicators_ilc) == NUM_INNER_LOOP_CONTROLLER


def test_get_indicator_color(widget: TabIlcStatus) -> None:
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Standby) == Qt.cyan
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Disabled) == Qt.blue
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Enabled) == Qt.green
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Fault) == Qt.red
    assert widget._get_indicator_color(MTM2.InnerLoopControlMode.Unknown) == Qt.gray


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
async def test_callback_signal_ilc_status_bypassed_ilcs(
    qtbot: QtBot, widget: TabIlcStatus
) -> None:

    bypassed_ilcs = [1, 2, 3]
    widget.model.signal_ilc_status.bypassed_ilcs.emit(bypassed_ilcs)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._label_bypassed_ilcs.text() == str(bypassed_ilcs)


def test_read_ilc_details_file(widget: TabIlcStatus) -> None:
    widget.read_ilc_details_file(get_ilc_details_file())

    assert widget._indicators_ilc[0].toolTip() == "Axial actuator: B1"
    assert widget._indicators_ilc[-1].toolTip() == "Inclinometer"
