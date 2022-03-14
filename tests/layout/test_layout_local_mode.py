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

from PySide2 import QtCore
from PySide2.QtWidgets import QWidget

from lsst.ts.m2gui import Model, LocalMode
from lsst.ts.m2gui.signal import SignalControl
from lsst.ts.m2gui.layout import LayoutLocalMode


class MockWidget(QWidget):
    def __init__(self):
        super().__init__()

        model = Model()
        signal_control = SignalControl()
        self.layout_local_mode = LayoutLocalMode(model, model.log, signal_control)

        self.setLayout(self.layout_local_mode.layout)


@pytest.fixture
def widget(qtbot):

    widget = MockWidget()
    qtbot.addWidget(widget)

    return widget


def test_callback_signal_control_normal(qtbot, widget):
    widget.layout_local_mode._signal_control.is_control_updated.emit(True)

    assert widget.layout_local_mode._button_standby.isEnabled() is False
    assert widget.layout_local_mode._button_diagnostic.isEnabled() is True
    assert widget.layout_local_mode._button_enable.isEnabled() is True


def test_callback_signal_control_prohibit_control(qtbot, widget):
    # CSC has the control
    widget.layout_local_mode.model.is_csc_commander = True

    widget.layout_local_mode._signal_control.is_control_updated.emit(True)

    _assert_prohibit_transition(widget)

    # System is in the closed-loop control
    widget.layout_local_mode.model.is_csc_commander = False
    widget.layout_local_mode.model.is_closed_loop = True

    widget.layout_local_mode._signal_control.is_control_updated.emit(True)

    _assert_prohibit_transition(widget)


def _assert_prohibit_transition(widget):
    assert widget.layout_local_mode._button_standby.isEnabled() is False
    assert widget.layout_local_mode._button_diagnostic.isEnabled() is False
    assert widget.layout_local_mode._button_enable.isEnabled() is False


def test_set_local_mode(qtbot, widget):
    qtbot.mouseClick(widget.layout_local_mode._button_diagnostic, QtCore.Qt.LeftButton)
    assert widget.layout_local_mode.model.local_mode == LocalMode.Diagnostic

    assert widget.layout_local_mode._button_standby.isEnabled() is True
    assert widget.layout_local_mode._button_diagnostic.isEnabled() is False
    assert widget.layout_local_mode._button_enable.isEnabled() is True

    qtbot.mouseClick(widget.layout_local_mode._button_enable, QtCore.Qt.LeftButton)
    assert widget.layout_local_mode.model.local_mode == LocalMode.Enable

    assert widget.layout_local_mode._button_standby.isEnabled() is True
    assert widget.layout_local_mode._button_diagnostic.isEnabled() is True
    assert widget.layout_local_mode._button_enable.isEnabled() is False

    qtbot.mouseClick(widget.layout_local_mode._button_diagnostic, QtCore.Qt.LeftButton)
    qtbot.mouseClick(widget.layout_local_mode._button_standby, QtCore.Qt.LeftButton)
    assert widget.layout_local_mode.model.local_mode == LocalMode.Standby

    assert widget.layout_local_mode._button_standby.isEnabled() is False
    assert widget.layout_local_mode._button_diagnostic.isEnabled() is True
    assert widget.layout_local_mode._button_enable.isEnabled() is True
