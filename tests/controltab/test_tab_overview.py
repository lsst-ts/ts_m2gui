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

from PySide2 import QtCore

from lsst.ts.m2gui import Model, LocalMode
from lsst.ts.m2gui.signal import SignalMessage
from lsst.ts.m2gui.controltab import TabOverview


@pytest.fixture
def widget(qtbot):

    widget = TabOverview("Overview")
    widget.set_model(Model(logging.getLogger()))
    widget.set_signal_message(SignalMessage())
    qtbot.addWidget(widget)

    return widget


def test_init(qtbot, widget):

    assert widget._label_control.text() == "Commander is: EUI"
    assert widget._label_control_mode.text() == "Control Mode: Standby"
    assert widget._label_local_mode.text() == "Control Loop: Open-Loop Control"

    assert widget._window_log.isReadOnly() is True
    assert widget._window_log.placeholderText() == "Log Message"


def test_update_control_status(qtbot, widget):

    widget.model.is_csc_commander = True
    widget.model.local_mode = LocalMode.Enable
    widget.model.is_closed_loop = True
    widget._update_control_status()

    assert widget._label_control.text() == "Commander is: CSC"
    assert widget._label_control_mode.text() == "Control Mode: Enable"
    assert widget._label_local_mode.text() == "Control Loop: Closed-Loop Control"


def test_callback_signal_message(qtbot, widget):

    assert widget._window_log.toPlainText() == ""

    message = "This is a test"
    widget._signal_message.message.emit(message)

    assert widget._window_log.toPlainText() == message


def test_callback_clear(qtbot, widget):

    message = "This is a test"
    widget._signal_message.message.emit(message)

    qtbot.mouseClick(widget._button_clear, QtCore.Qt.LeftButton)

    assert widget._window_log.toPlainText() == ""