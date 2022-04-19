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
from PySide2.QtGui import QPalette

from lsst.ts.m2gui import Model, LocalMode
from lsst.ts.m2gui.signal import SignalMessage
from lsst.ts.m2gui.controltab import TabOverview


@pytest.fixture
def widget(qtbot):

    widget = TabOverview("Overview", Model(logging.getLogger()))
    widget.set_signal_message(SignalMessage())
    qtbot.addWidget(widget)

    return widget


def test_init(qtbot, widget):

    assert widget._label_control.text() == "Commander is: EUI"
    assert widget._label_control_mode.text() == "Control Mode: Standby"
    assert widget._label_local_mode.text() == "Control Loop: Open-Loop Control"

    assert widget._window_log.isReadOnly() is True
    assert widget._window_log.placeholderText() == "Log Message"

    for indicator in widget._indicators_status.values():
        assert indicator.isEnabled() is False
        assert indicator.autoFillBackground() is True

        palette = indicator.palette()
        color = palette.color(QPalette.Button)

        assert color == Qt.gray


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

    qtbot.mouseClick(widget._button_clear, Qt.LeftButton)

    assert widget._window_log.toPlainText() == ""


def test_callback_signal_status(qtbot, widget):

    name = "isTelemetryActive"
    widget.model.update_system_status(name, True)

    palette = widget._indicators_status[name].palette()
    color = palette.color(QPalette.Button)

    assert color == Qt.green


def test_callback_signal_status_is_alarm_warning_on(qtbot, widget):

    # Default color
    assert _get_color_is_alarm_warning_on(widget) == Qt.gray

    # There is the error
    widget.model.add_error(3)

    assert _get_color_is_alarm_warning_on(widget) == Qt.red

    # The error is cleared
    widget.model.reset_errors()

    assert _get_color_is_alarm_warning_on(widget) == Qt.gray


def _get_color_is_alarm_warning_on(widget):

    palette = widget._indicators_status["isAlarmWarningOn"].palette()
    return palette.color(QPalette.Button)
