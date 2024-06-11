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
import pytest_asyncio
from lsst.ts.m2gui import ForceErrorTangent, Model
from lsst.ts.m2gui.controltab import TabDiagnostics
from lsst.ts.xml.enums import MTM2
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QPushButton
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabDiagnostics:
    widget = TabDiagnostics("Diagnostics", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest_asyncio.fixture
async def widget_async(qtbot: QtBot) -> TabDiagnostics:
    async with TabDiagnostics(
        "Diagnostics", Model(logging.getLogger(), is_simulation_mode=True)
    ) as widget_sim:
        qtbot.addWidget(widget_sim)

        await widget_sim.model.connect()
        yield widget_sim


# Need to add this to make the above widget_async() to work on Jenkins.
# I guess there is some bug in "pytest" and "pytest_asyncio" libraries.
def test_init(widget_async: TabDiagnostics) -> None:
    pass


@pytest.mark.asyncio
async def test_callback_control_digital_status(
    qtbot: QtBot, widget_async: TabDiagnostics
) -> None:
    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    # Should fail in the wrong state
    control = widget_async._digital_status_control[2]
    assert control.isChecked() is True
    assert control.text() == "ON"

    # Go to the Diagnostic state
    await widget_async.model.enter_diagnostic()

    qtbot.mouseClick(control, Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert control.isChecked() is False
    assert control.text() == "OFF"


@pytest.mark.asyncio
async def test_callback_power_motor_calibrated(widget: TabDiagnostics) -> None:
    widget.model.utility_monitor.update_power_calibrated(MTM2.PowerType.Motor, 0.1, 0.2)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._power_calibrated["power_voltage_motor"].text() == "0.1 V"
    assert widget._power_calibrated["power_current_motor"].text() == "0.2 A"


@pytest.mark.asyncio
async def test_callback_power_communication_calibrated(widget: TabDiagnostics) -> None:
    widget.model.utility_monitor.update_power_calibrated(
        MTM2.PowerType.Communication, 0.3, 0.4
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._power_calibrated["power_voltage_communication"].text() == "0.3 V"
    assert widget._power_calibrated["power_current_communication"].text() == "0.4 A"


@pytest.mark.asyncio
async def test_callback_power_motor_raw(widget: TabDiagnostics) -> None:
    widget.model.utility_monitor.update_power_raw(MTM2.PowerType.Motor, 0.5, 0.6)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._power_raw["power_voltage_motor"].text() == "0.5 V"
    assert widget._power_raw["power_current_motor"].text() == "0.6 A"


@pytest.mark.asyncio
async def test_callback_power_communication_raw(widget: TabDiagnostics) -> None:
    widget.model.utility_monitor.update_power_raw(
        MTM2.PowerType.Communication, 0.7, 0.8
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._power_raw["power_voltage_communication"].text() == "0.7 V"
    assert widget._power_raw["power_current_communication"].text() == "0.8 A"


@pytest.mark.asyncio
async def test_callback_digital_status_input(widget: TabDiagnostics) -> None:
    widget.model.utility_monitor.update_digital_status_input(3)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    _assert_indicator_color(widget._digital_status_input[0], Qt.green)
    _assert_indicator_color(widget._digital_status_input[1], Qt.green)
    _assert_indicator_color(widget._digital_status_input[2], Qt.gray)


def _assert_indicator_color(indicator: QPushButton, target_color: QColor) -> None:
    palette = indicator.palette()
    assert palette.color(QPalette.Button) == target_color


@pytest.mark.asyncio
async def test_callback_digital_status_output(widget: TabDiagnostics) -> None:
    widget.model.utility_monitor.update_digital_status_output(6)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

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


@pytest.mark.asyncio
async def test_callback_force_error_tangent(widget: TabDiagnostics) -> None:
    force_error_tangent = ForceErrorTangent()
    force_error_tangent.error_force = [1.2, -2000.233, -1.334, 0, 31.34, -2.29]
    force_error_tangent.error_weight = 13.331
    force_error_tangent.error_sum = -1200.452
    widget.model.utility_monitor.update_force_error_tangent(force_error_tangent)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert (
        widget._force_error_tangent["a1"].text() == "<font color='black'>1.2 N</font>"
    )
    assert (
        widget._force_error_tangent["a2"].text() == "<font color='red'>-2000.2 N</font>"
    )
    assert (
        widget._force_error_tangent["a3"].text() == "<font color='black'>-1.3 N</font>"
    )
    assert widget._force_error_tangent["a4"].text() == "<font color='black'>0 N</font>"
    assert (
        widget._force_error_tangent["a5"].text() == "<font color='black'>31.3 N</font>"
    )
    assert (
        widget._force_error_tangent["a6"].text() == "<font color='black'>-2.3 N</font>"
    )

    assert (
        widget._force_error_tangent["total_weight"].text()
        == "<font color='black'>13.3 N</font>"
    )
    assert (
        widget._force_error_tangent["tangent_sum"].text()
        == "<font color='red'>-1200.5 N</font>"
    )
