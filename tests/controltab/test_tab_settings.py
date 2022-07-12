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
import logging

from PySide2.QtCore import Qt

from lsst.ts.m2gui import Model
from lsst.ts.m2gui.controltab import TabSettings


@pytest.fixture
def widget(qtbot):

    widget = TabSettings("Settings", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget):

    assert widget._settings["host"].text() == widget.model.host
    assert widget._settings["port_command"].value() == widget.model.port_command
    assert widget._settings["port_telemetry"].value() == widget.model.port_telemetry
    assert (
        widget._settings["timeout_connection"].value()
        == widget.model.timeout_connection
    )

    for port in ("port_command", "port_telemetry"):
        assert widget._settings[port].minimum() == widget.PORT_MINIMUM
        assert widget._settings[port].maximum() == widget.PORT_MAXIMUM

    assert widget._settings["timeout_connection"].minimum() == widget.TIMEOUT_MINIMUM

    line_edit = widget._settings["host"]
    font_metrics = line_edit.fontMetrics()
    assert (
        line_edit.minimumWidth()
        == font_metrics.boundingRect(line_edit.text()).width() + 20
    )


def test_callback_apply(qtbot, widget):

    widget._settings["host"].setText("newHost")
    widget._settings["port_command"].setValue(1)
    widget._settings["port_telemetry"].setValue(2)
    widget._settings["timeout_connection"].setValue(3)

    qtbot.mouseClick(widget._button_apply, Qt.LeftButton)

    assert widget.model.host == "newHost"
    assert widget.model.port_command == 1
    assert widget.model.port_telemetry == 2
    assert widget.model.timeout_connection == 3
