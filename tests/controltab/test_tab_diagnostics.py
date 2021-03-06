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

from lsst.ts.m2gui import Model, ForceErrorTangent, LocalMode, PowerType
from lsst.ts.m2gui.controltab import TabDiagnostics


@pytest.fixture
def widget(qtbot):

    widget = TabDiagnostics("Diagnostics", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_callback_control_digital_status(qtbot, widget):

    widget.model.local_mode = LocalMode.Diagnostic

    control = widget._digital_status_control[2]
    assert control.isChecked() is False
    assert control.text() == "OFF"

    qtbot.mouseClick(control, Qt.LeftButton)

    assert control.isChecked() is True
    assert control.text() == "ON"


def test_callback_power_motor_calibrated(widget):

    widget.model.utility_monitor.update_power_calibrated(PowerType.Motor, 0.1, 0.2)
    assert widget._power_calibrated["power_voltage_motor"].text() == "0.1 V"
    assert widget._power_calibrated["power_current_motor"].text() == "0.2 A"


def test_callback_power_communication_calibrated(widget):

    widget.model.utility_monitor.update_power_calibrated(
        PowerType.Communication, 0.3, 0.4
    )
    assert widget._power_calibrated["power_voltage_communication"].text() == "0.3 V"
    assert widget._power_calibrated["power_current_communication"].text() == "0.4 A"


def test_callback_power_motor_raw(widget):

    widget.model.utility_monitor.update_power_raw(PowerType.Motor, 0.5, 0.6)
    assert widget._power_raw["power_voltage_motor"].text() == "0.5 V"
    assert widget._power_raw["power_current_motor"].text() == "0.6 A"


def test_callback_power_communication_raw(widget):

    widget.model.utility_monitor.update_power_raw(PowerType.Communication, 0.7, 0.8)
    assert widget._power_raw["power_voltage_communication"].text() == "0.7 V"
    assert widget._power_raw["power_current_communication"].text() == "0.8 A"


def test_callback_digital_status_input(widget):

    widget.model.utility_monitor.update_digital_status_input(3)

    _assert_indicator_color(widget._digital_status_input[0], Qt.green)
    _assert_indicator_color(widget._digital_status_input[1], Qt.green)
    _assert_indicator_color(widget._digital_status_input[2], Qt.gray)


def _assert_indicator_color(indicator, target_color):

    palette = indicator.palette()
    assert palette.color(QPalette.Button) == target_color


def test_callback_digital_status_output(widget):

    widget.model.utility_monitor.update_digital_status_output(6)

    _assert_indicator_color(widget._digital_status_output[0], Qt.gray)
    _assert_indicator_color(widget._digital_status_output[1], Qt.green)
    _assert_indicator_color(widget._digital_status_output[2], Qt.green)
    _assert_indicator_color(widget._digital_status_output[3], Qt.gray)

    assert widget._digital_status_control[0].isChecked() is False
    assert widget._digital_status_control[1].isChecked() is True
    assert widget._digital_status_control[2].isChecked() is True
    assert widget._digital_status_control[3].isChecked() is False

    assert widget._digital_status_control[0].text() == "OFF"
    assert widget._digital_status_control[1].text() == "ON"
    assert widget._digital_status_control[2].text() == "ON"
    assert widget._digital_status_control[3].text() == "OFF"


def test_callback_force_error_tangent(widget):

    force_error_tangent = ForceErrorTangent()
    force_error_tangent.error_force = [1.2, 0.233, -1.334, 0, 31.34, -2.29]
    force_error_tangent.error_weight = 13.331
    force_error_tangent.error_sum = 12.452
    widget.model.utility_monitor.update_force_error_tangent(force_error_tangent)

    assert widget._force_error_tangent["a1"].text() == "1.2 N"
    assert widget._force_error_tangent["a2"].text() == "0.2 N"
    assert widget._force_error_tangent["a3"].text() == "-1.3 N"
    assert widget._force_error_tangent["a4"].text() == "0 N"
    assert widget._force_error_tangent["a5"].text() == "31.3 N"
    assert widget._force_error_tangent["a6"].text() == "-2.3 N"

    assert widget._force_error_tangent["total_weight"].text() == "13.3 N"
    assert widget._force_error_tangent["tangent_sum"].text() == "12.5 N"
