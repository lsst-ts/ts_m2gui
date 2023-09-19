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
from lsst.ts.m2gui import LocalMode, Model, SignalMessage
from lsst.ts.m2gui.controltab import TabOverview
from lsst.ts.xml.enums import MTM2
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QPalette
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabOverview:
    widget = TabOverview("Overview", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest_asyncio.fixture
async def widget_async(qtbot: QtBot) -> TabOverview:
    async with TabOverview(
        "Overview", Model(logging.getLogger(), is_simulation_mode=True)
    ) as widget_sim:
        qtbot.addWidget(widget_sim)

        await widget_sim.model.connect()
        yield widget_sim


def test_init(qtbot: QtBot, widget: TabOverview) -> None:
    assert widget._label_control.text() == "Commander is: EUI"
    assert widget._label_control_mode.text() == "Control Mode: Standby"
    assert widget._label_local_mode.text() == "Control Loop: Open-Loop Control"
    assert widget._label_inclination_source.text() == "Inclination Source: ONBOARD"

    assert widget._window_log.isReadOnly() is True
    assert widget._window_log.placeholderText() == "Log Message"

    for indicator in widget._indicators_status.values():
        assert indicator.isEnabled() is False
        assert indicator.autoFillBackground() is True

        palette = indicator.palette()
        color = palette.color(QPalette.Button)

        assert color == Qt.gray


def test_update_control_status(qtbot: QtBot, widget: TabOverview) -> None:
    widget.model.is_csc_commander = True
    widget.model.local_mode = LocalMode.Enable
    widget.model.is_closed_loop = True
    widget.model.inclination_source = MTM2.InclinationTelemetrySource.MTMOUNT
    widget._update_control_status()

    assert widget._label_control.text() == "Commander is: CSC"
    assert widget._label_control_mode.text() == "Control Mode: Enable"
    assert widget._label_local_mode.text() == "Control Loop: Closed-Loop Control"
    assert widget._label_inclination_source.text() == "Inclination Source: MTMOUNT"


@pytest.mark.asyncio
async def test_callback_signal_message(qtbot: QtBot, widget: TabOverview) -> None:
    assert widget._window_log.toPlainText() == ""

    signal_message = SignalMessage()
    widget.set_signal_message(signal_message)

    message = "This is a test"
    signal_message.message.emit(message)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._window_log.toPlainText() == message


def test_callback_clear(qtbot: QtBot, widget: TabOverview) -> None:
    signal_message = SignalMessage()
    widget.set_signal_message(signal_message)

    message = "This is a test"
    signal_message.message.emit(message)

    qtbot.mouseClick(widget._button_clear, Qt.LeftButton)

    assert widget._window_log.toPlainText() == ""


@pytest.mark.asyncio
async def test_callback_signal_status(qtbot: QtBot, widget: TabOverview) -> None:
    name = "isTelemetryActive"
    widget.model.update_system_status(name, True)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    palette = widget._indicators_status[name].palette()
    color = palette.color(QPalette.Button)

    assert color == Qt.green


@pytest.mark.asyncio
async def test_callback_signal_status_is_alarm_on(
    qtbot: QtBot, widget_async: TabOverview
) -> None:
    # Default color
    assert _get_color_is_alarm_on(widget_async) == Qt.gray

    # There is the error
    widget_async.model.controller.error_handler.add_new_error(3)
    widget_async.model.report_error(3)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert _get_color_is_alarm_on(widget_async) == Qt.red

    # The error is cleared
    await widget_async.model.reset_errors()

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert _get_color_is_alarm_on(widget_async) == Qt.gray


def _get_color_is_alarm_on(widget: TabOverview) -> QColor:
    palette = widget._indicators_status["isAlarmOn"].palette()
    return palette.color(QPalette.Button)


@pytest.mark.asyncio
async def test_callback_signal_status_is_warning_on(
    qtbot: QtBot, widget_async: TabOverview
) -> None:
    # Default color
    assert _get_color_is_warning_on(widget_async) == Qt.gray

    # There is the warning
    widget_async.model.controller.error_handler.add_new_warning(3)
    widget_async.model.report_error(3)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert _get_color_is_warning_on(widget_async) == Qt.yellow

    # The warning is cleared
    await widget_async.model.reset_errors()

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert _get_color_is_warning_on(widget_async) == Qt.gray


def _get_color_is_warning_on(widget: TabOverview) -> QColor:
    palette = widget._indicators_status["isWarningOn"].palette()
    return palette.color(QPalette.Button)
