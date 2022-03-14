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
from lsst.ts.m2gui.layout import LayoutControl


class MockWidget(QWidget):
    def __init__(self):
        super().__init__()

        model = Model()
        signal_control = SignalControl()
        self.layout_control = LayoutControl(model, model.log, signal_control)

        self.setLayout(self.layout_control.layout)


@pytest.fixture
def widget(qtbot):

    widget = MockWidget()
    qtbot.addWidget(widget)

    return widget


def test_callback_signal_control_normal(qtbot, widget):
    widget.layout_control._signal_control.is_control_updated.emit(True)

    assert widget.layout_control._button_remote.isEnabled() is True
    assert widget.layout_control._button_local.isEnabled() is False


def test_callback_signal_control_prohibit_control(qtbot, widget):
    widget.layout_control.model.local_mode = LocalMode.Diagnostic

    widget.layout_control._signal_control.is_control_updated.emit(True)

    assert widget.layout_control._button_remote.isEnabled() is False
    assert widget.layout_control._button_local.isEnabled() is False


def test_set_csc_commander(qtbot, widget):
    widget.layout_control.set_csc_commander(True)
    assert widget.layout_control.model.is_csc_commander is True
    assert widget.layout_control._button_remote.isEnabled() is False
    assert widget.layout_control._button_local.isEnabled() is True

    qtbot.mouseClick(widget.layout_control._button_local, QtCore.Qt.LeftButton)
    assert widget.layout_control.model.is_csc_commander is False
    assert widget.layout_control._button_remote.isEnabled() is True
    assert widget.layout_control._button_local.isEnabled() is False

    qtbot.mouseClick(widget.layout_control._button_remote, QtCore.Qt.LeftButton)
    assert widget.layout_control.model.is_csc_commander is True
    assert widget.layout_control._button_remote.isEnabled() is False
    assert widget.layout_control._button_local.isEnabled() is True
