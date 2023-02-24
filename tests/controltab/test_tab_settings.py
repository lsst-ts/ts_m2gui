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
from lsst.ts.m2gui.controltab import TabSettings
from PySide2.QtCore import Qt
from qasync import QApplication


@pytest.fixture
def widget(qtbot):
    widget = TabSettings("Settings", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget):
    controller = widget.model.controller
    assert widget._settings["host"].text() == controller.host
    assert widget._settings["port_command"].value() == controller.port_command
    assert widget._settings["port_telemetry"].value() == controller.port_telemetry
    assert (
        widget._settings["timeout_connection"].value() == controller.timeout_connection
    )
    assert widget._settings["log_level"].value() == widget.model.log.level
    assert widget._settings["refresh_frequency"].value() == int(
        1000 / widget.model.duration_refresh
    )

    app = QApplication.instance()
    assert widget._settings["point_size"].value() == app.font().pointSize()

    for port in ("port_command", "port_telemetry"):
        assert widget._settings[port].minimum() == widget.PORT_MINIMUM
        assert widget._settings[port].maximum() == widget.PORT_MAXIMUM

    assert widget._settings["timeout_connection"].minimum() == widget.TIMEOUT_MINIMUM

    assert widget._settings["log_level"].minimum() == widget.LOG_LEVEL_MINIMUM
    assert widget._settings["log_level"].maximum() == widget.LOG_LEVEL_MAXIMUM

    line_edit = widget._settings["host"]
    font_metrics = line_edit.fontMetrics()
    assert (
        line_edit.minimumWidth()
        == font_metrics.boundingRect(line_edit.text()).width() + 20
    )

    assert (
        widget._settings["refresh_frequency"].minimum()
        == widget.REFRESH_FREQUENCY_MINIMUM
    )
    assert (
        widget._settings["refresh_frequency"].maximum()
        == widget.REFRESH_FREQUENCY_MAXIMUM
    )

    assert widget._settings["point_size"].minimum() == widget.POINT_SIZE_MINIMUM
    assert widget._settings["point_size"].maximum() == widget.POINT_SIZE_MAXIMUM


@pytest.mark.asyncio
async def test_callback_apply_host(qtbot, widget):
    widget._settings["host"].setText("newHost")
    widget._settings["port_command"].setValue(1)
    widget._settings["port_telemetry"].setValue(2)
    widget._settings["timeout_connection"].setValue(3)

    qtbot.mouseClick(widget._button_apply_host, Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    controller = widget.model.controller
    assert controller.host == "newHost"
    assert controller.port_command == 1
    assert controller.port_telemetry == 2
    assert controller.timeout_connection == 3


@pytest.mark.asyncio
async def test_callback_apply_general(qtbot, widget):
    widget._settings["log_level"].setValue(11)
    widget._settings["refresh_frequency"].setValue(5)
    widget._settings["point_size"].setValue(12)

    qtbot.mouseClick(widget._button_apply_general, Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget.model.log.level == 11
    assert widget.model.duration_refresh == 200

    app = QApplication.instance()
    assert app.font().pointSize() == 12
