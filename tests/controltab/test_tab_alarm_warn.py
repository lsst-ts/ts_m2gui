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
import pathlib

from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette

from lsst.ts.m2gui import Model, LimitSwitchType, Ring
from lsst.ts.m2gui.controltab import TabAlarmWarn


def get_error_list_file():
    policy_dir = pathlib.Path(__file__).parents[0] / ".." / ".." / "policy"

    return policy_dir / "error_code_m2.tsv"


@pytest.fixture
def widget(qtbot):

    widget = TabAlarmWarn("Alarms/Warnings", Model(logging.getLogger()))
    widget.read_error_list_file(get_error_list_file())

    qtbot.addWidget(widget)

    return widget


def test_init(qtbot, widget):

    assert len(widget._error_list) == 39
    assert len(widget._error_list["6051"]) == 6

    assert widget._text_error_cause.placeholderText() == "Possible Error Cause"
    assert widget._text_error_cause.isReadOnly() is True

    for limit_switch_status in (
        widget._indicators_limit_switch_retract,
        widget._indicators_limit_switch_extend,
    ):
        for indicator in limit_switch_status.values():
            assert indicator.isEnabled() is False
            assert indicator.autoFillBackground() is True

            palette = indicator.palette()
            color = palette.color(QPalette.Button)

            assert color == Qt.green


def test_callback_selection_changed(qtbot, widget):

    assert widget._text_error_cause.toPlainText() == ""

    # Select the first error code
    center = _get_widget_item_center(widget, "6054")
    qtbot.mouseClick(
        widget._table_error.viewport(),
        Qt.LeftButton,
        pos=center,
    )

    assert (
        widget._text_error_cause.toPlainText()
        == "Internal ILC issue. ILC did not change state"
    )

    # Select the second error code
    center = _get_widget_item_center(widget, "6052")
    qtbot.mouseClick(
        widget._table_error.viewport(),
        Qt.LeftButton,
        pos=center,
    )

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

    assert (
        widget._text_error_cause.toPlainText()
        == "ILC responded with an exception code or did not respond at all (timeout)"
    )


def _get_widget_item_center(widget, item_text):

    items = widget._table_error.findItems(item_text, Qt.MatchExactly)
    rect = widget._table_error.visualItemRect(items[0])
    return rect.center()


def test_callback_signal_error_new(qtbot, widget):

    widget.model.add_error(6051)

    color_6051 = _get_widget_item_color(widget, "6051")
    assert color_6051 == Qt.red

    widget.model.add_error(6052)

    color_6052 = _get_widget_item_color(widget, "6052")
    assert color_6052 == Qt.yellow


def _get_widget_item_color(widget, item_text):

    items = widget._table_error.findItems(item_text, Qt.MatchExactly)
    return items[0].background().color()


def test_callback_signal_error_cleared(qtbot, widget):

    widget.model.add_error(6051)

    widget.model.clear_error(6051)

    # Color should be white
    color_6051 = _get_widget_item_color(widget, "6051")
    assert color_6051 == Qt.white


def test_callback_reset(qtbot, widget):

    # Update the text of error cause
    center = _get_widget_item_center(widget, "6054")
    qtbot.mouseClick(
        widget._table_error.viewport(),
        Qt.LeftButton,
        pos=center,
    )

    # Highlight the error
    widget.model.add_error(6051)

    # Trigger the limit switch
    widget.model.fault_manager.update_limit_switch_status(
        LimitSwitchType.Extend, Ring.C, 3, True
    )

    # Click the reset button
    qtbot.mouseClick(widget._button_reset, Qt.LeftButton)

    # Check the text of error cause should be cleared
    assert widget._text_error_cause.toPlainText() == ""

    # Check the color of error code should be default
    color_6051 = _get_widget_item_color(widget, "6051")
    assert color_6051 == Qt.white

    assert widget.model.fault_manager.errors == set()

    # Check the color of limit switch should be default
    indicator = widget._indicators_limit_switch_extend["C3"]
    palette = indicator.palette()
    color = palette.color(QPalette.Button)

    assert color == Qt.green


def test_set_error_item_color_error(qtbot, widget):

    with pytest.raises(ValueError):
        widget._set_error_item_color(None, "wrong_status")


def test_callback_signal_limit_switch(qtbot, widget):

    widget.model.fault_manager.update_limit_switch_status(
        LimitSwitchType.Extend, Ring.C, 3, True
    )

    indicator = widget._indicators_limit_switch_extend["C3"]
    palette = indicator.palette()
    color = palette.color(QPalette.Button)

    assert color == Qt.red
