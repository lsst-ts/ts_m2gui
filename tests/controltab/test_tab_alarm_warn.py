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
import pytest_asyncio
from lsst.ts.m2com import DEFAULT_ENABLED_FAULTS_MASK, LimitSwitchType, get_config_dir
from lsst.ts.m2gui import LocalMode, Model, Ring, Status
from lsst.ts.m2gui.controltab import TabAlarmWarn
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QPalette
from pytestqt.qtbot import QtBot

SLEEP_TIME_SHORT = 1
SLEEP_TIME_LONG = 5


def get_error_list_file() -> Path:
    return get_config_dir() / "error_code.tsv"


@pytest.fixture
def widget(qtbot: QtBot) -> TabAlarmWarn:
    widget = TabAlarmWarn("Alarms/Warnings", Model(logging.getLogger()))
    widget.read_error_list_file(get_error_list_file())

    qtbot.addWidget(widget)

    return widget


@pytest_asyncio.fixture
async def widget_async(qtbot: QtBot) -> TabAlarmWarn:
    async with TabAlarmWarn(
        "Alarms/Warnings", Model(logging.getLogger(), is_simulation_mode=True)
    ) as widget_sim:
        widget_sim.read_error_list_file(get_error_list_file())
        qtbot.addWidget(widget_sim)

        await widget_sim.model.connect()
        yield widget_sim


def test_init(widget: TabAlarmWarn) -> None:
    assert len(widget._error_list) == 37
    assert len(widget._error_list["6051"]) == 6
    assert list(widget._error_list.keys())[-1] == "6088"

    assert widget._text_error_cause.placeholderText() == "Possible Error Cause"
    assert widget._text_error_cause.isReadOnly() is True


@pytest.mark.asyncio
async def test_callback_button_limit_switch_status(qtbot: QtBot, widget: TabAlarmWarn) -> None:
    assert widget._tab_limit_switch_status.isVisible() is False

    qtbot.mouseClick(widget._button_limit_switch_status, Qt.LeftButton)

    assert widget._tab_limit_switch_status.isVisible() is True


@pytest.mark.asyncio
async def test_callback_selection_changed(qtbot: QtBot, widget: TabAlarmWarn) -> None:
    assert widget._text_error_cause.toPlainText() == ""

    # Select the first error code
    center = _get_widget_item_center(widget, "6054")
    qtbot.mouseClick(
        widget._table_error.viewport(),
        Qt.LeftButton,
        pos=center,
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    assert widget._text_error_cause.toPlainText() == "Internal ILC issue. ILC did not change state"

    # Select the second error code
    center = _get_widget_item_center(widget, "6052")
    qtbot.mouseClick(
        widget._table_error.viewport(),
        Qt.LeftButton,
        pos=center,
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    assert (
        widget._text_error_cause.toPlainText()
        == "ILC responded with an exception code or did not respond at all (timeout)"
    )

    # There should be no change of text
    center = _get_widget_item_center(widget, "Actuator ILC Read Error")
    qtbot.mouseClick(
        widget._table_error.viewport(),
        Qt.LeftButton,
        pos=center,
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    assert (
        widget._text_error_cause.toPlainText()
        == "ILC responded with an exception code or did not respond at all (timeout)"
    )


def _get_widget_item_center(widget: TabAlarmWarn, item_text: str) -> QPoint:
    items = widget._table_error.findItems(item_text, Qt.MatchExactly)
    rect = widget._table_error.visualItemRect(items[0])
    return rect.center()


def test_get_selected_error_codes(widget: TabAlarmWarn) -> None:
    # No selected item
    assert widget._get_selected_error_codes() == set()

    # There are selected items
    for row in range(2):
        for column in range(2):
            widget._table_error.item(row, column).setSelected(True)

    assert widget._get_selected_error_codes() == {6051, 6052}


@pytest.mark.asyncio
async def test_is_diagnostic_mode(widget: TabAlarmWarn) -> None:
    widget.model.local_mode = LocalMode.Diagnostic

    is_diagnostic_mode = await widget._is_diagnostic_mode()

    assert is_diagnostic_mode is True


@pytest.mark.asyncio
async def test_callback_signal_summary_faults_status(qtbot: QtBot, widget: TabAlarmWarn) -> None:
    # Test the maximum value of U64
    widget.model.fault_manager.update_summary_faults_status(18446744073709551615)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    assert widget._label_summary_faults_status.text() == "0xffffffffffffffff"


@pytest.mark.asyncio
async def test_callback_signal_enabled_faults_mask_default(qtbot: QtBot, widget: TabAlarmWarn) -> None:
    # Test the maximum value of U64
    widget.model.fault_manager.report_enabled_faults_mask(DEFAULT_ENABLED_FAULTS_MASK)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    assert widget._label_enabled_faults_mask.text() == hex(DEFAULT_ENABLED_FAULTS_MASK)
    assert widget._label_error_code_bypass.text() == "None"


@pytest.mark.asyncio
async def test_callback_signal_enabled_faults_mask_bypassed(qtbot: QtBot, widget: TabAlarmWarn) -> None:
    # Test the maximum value of U64
    # bit 5: 6057, bit 6: 6056
    mask = DEFAULT_ENABLED_FAULTS_MASK - 2**5 - 2**6
    widget.model.fault_manager.report_enabled_faults_mask(mask)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    assert widget._label_enabled_faults_mask.text() == hex(mask)
    assert widget._label_error_code_bypass.text() == "<font color='red'>[6056, 6057]</font>"


@pytest.mark.asyncio
async def test_callback_signal_error_new(qtbot: QtBot, widget: TabAlarmWarn) -> None:
    widget.model.report_error(6051)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    color_6051 = _get_widget_item_color(widget, "6051")
    assert color_6051 == Qt.red

    widget.model.report_error(6052)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    color_6052 = _get_widget_item_color(widget, "6052")
    assert color_6052 == Qt.yellow


def _get_widget_item_color(widget: TabAlarmWarn, item_text: str) -> QColor:
    items = widget._table_error.findItems(item_text, Qt.MatchExactly)
    return items[0].background().color()


@pytest.mark.asyncio
async def test_callback_signal_error_cleared(qtbot: QtBot, widget: TabAlarmWarn) -> None:
    widget.model.report_error(6051)

    widget.model.clear_error(6051)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    # Color should be white
    color_6051 = _get_widget_item_color(widget, "6051")
    assert color_6051 == Qt.white


@pytest.mark.asyncio
async def test_callback_reset(qtbot: QtBot, widget_async: TabAlarmWarn) -> None:
    # Update the text of error cause
    center = _get_widget_item_center(widget_async, "6054")
    qtbot.mouseClick(
        widget_async._table_error.viewport(),
        Qt.LeftButton,
        pos=center,
    )

    # Highlight the error
    widget_async.model.report_error(6051)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_SHORT)

    # Trigger the limit switch
    widget_async.model.fault_manager.update_limit_switch_status(
        LimitSwitchType.Extend, Ring.C, 3, Status.Error
    )

    # Click the reset button
    qtbot.mouseClick(widget_async._button_reset, Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(SLEEP_TIME_LONG)

    # Check the text of error cause should be cleared
    assert widget_async._text_error_cause.toPlainText() == ""

    # Check the color of error code should be default
    color_6051 = _get_widget_item_color(widget_async, "6051")
    assert color_6051 == Qt.white

    assert widget_async.model.fault_manager.errors == set()

    # Check the color of limit switch should be default
    indicator = widget_async._tab_limit_switch_status._indicators_limit_switch_extend["C3"]
    palette = indicator.palette()
    color = palette.color(QPalette.Button)

    assert color == Qt.green


def test_set_error_item_color_error(qtbot: QtBot, widget: TabAlarmWarn) -> None:
    with pytest.raises(ValueError):
        widget._set_error_item_color(None, "wrong_status")
