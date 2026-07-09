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

import logging

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette
from pytestqt.qtbot import QtBot

from lsst.ts.m2com import NUM_ACTUATOR
from lsst.ts.m2gui import Model
from lsst.ts.m2gui.controltab import TabIlc
from lsst.ts.xml.enums import MTM2


@pytest.fixture
def widget(qtbot: QtBot) -> TabIlc:
    widget = TabIlc("ILC", Model(logging.getLogger()), NUM_ACTUATOR)
    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def widget_monitor(qtbot: QtBot) -> TabIlc:
    widget_monitor = TabIlc("ILC", Model(logging.getLogger()), NUM_ACTUATOR + 1)
    qtbot.addWidget(widget_monitor)

    return widget_monitor


def test_init(widget: TabIlc) -> None:
    assert widget._command_parameters["mode"].count() == 7

    for name in ["calibration_data", "get_rate", "set_rate", "set_offset_and_sensitivity"]:
        assert widget._commands[name].isEnabled() is True

    assert widget._command_parameters["rate"].maximum() == 12
    assert widget._command_parameters["rate"].minimum() == 0

    assert widget._command_parameters["channel"].maximum() == 4
    assert widget._command_parameters["channel"].minimum() == 1

    assert widget._command_parameters["offset"].maximum() == 100.0
    assert widget._command_parameters["offset"].minimum() == -100.0

    assert widget._command_parameters["sensitivity"].maximum() == 10.0
    assert widget._command_parameters["sensitivity"].minimum() == 0.0


def test_init_monitor(widget_monitor: TabIlc) -> None:
    assert widget_monitor._command_parameters["mode"].count() == 6

    for name in ["calibration_data", "get_rate", "set_rate", "set_offset_and_sensitivity"]:
        assert widget_monitor._commands[name].isEnabled() is False


def test_update_offset_and_sensitivity_based_on_channel(widget: TabIlc) -> None:
    widget._labels["main_offset_2"].setText("10.00001")
    widget._labels["main_sensitivity_2"].setText("5.00002")
    widget._command_parameters["channel"].setValue(2)

    widget._update_offset_and_sensitivity_based_on_channel()

    assert widget._command_parameters["offset"].value() == 10.00001
    assert widget._command_parameters["sensitivity"].value() == 5.00002


def test_is_actuator_ilc(widget: TabIlc) -> None:
    assert widget.is_actuator_ilc() is True


def test_is_actuator_ilc_monitor(widget_monitor: TabIlc) -> None:
    assert widget_monitor.is_actuator_ilc() is False


def test_get_mode(widget: TabIlc) -> None:
    assert widget._get_mode() == MTM2.InnerLoopControlMode.Standby

    widget._command_parameters["mode"].setCurrentIndex(1)
    assert widget._get_mode() == MTM2.InnerLoopControlMode.Disabled


def test_get_mode_monitor(widget_monitor: TabIlc) -> None:
    assert widget_monitor._get_mode() == MTM2.InnerLoopControlMode.Standby

    widget_monitor._command_parameters["mode"].setCurrentIndex(1)
    assert widget_monitor._get_mode() == MTM2.InnerLoopControlMode.Enabled


def test_get_zero_based_channel_offset_sensitivity(widget: TabIlc) -> None:
    widget._command_parameters["channel"].setValue(3)
    widget._command_parameters["offset"].setValue(-50.0)
    widget._command_parameters["sensitivity"].setValue(5.0)

    channel, offset, sensitivity = widget._get_zero_based_channel_offset_sensitivity()

    assert channel == 2
    assert offset == -50.0
    assert sensitivity == 5.0


def test_get_selected_command(widget: TabIlc) -> None:
    assert widget._get_selected_command() == "set_mode"

    widget._commands["reset"].setChecked(True)
    assert widget._get_selected_command() == "reset"


def test_set_server_id(widget: TabIlc) -> None:
    widget.set_server_id(1, 4, 3, 4, 5, "1.2", "Unknown")

    assert widget._labels["unique_id"].text() == "1"
    assert widget._labels["application_type"].text() == "Temperature Monitor (4)"
    assert widget._labels["network_node_type"].text() == "3"
    assert widget._labels["selected_options"].text() == "4"
    assert widget._labels["network_node_options"].text() == "5"
    assert widget._labels["firmware_revision"].text() == "1.2"
    assert widget._labels["firmware_name"].text() == "Unknown"


def test_set_server_status(widget: TabIlc) -> None:
    widget.set_server_status(MTM2.InnerLoopControlMode.Disabled)

    assert widget._labels["mode"].text() == "Disabled"
    assert widget._labels["status"].text() == "0x0"
    assert widget._labels["faults"].text() == "0x0"

    widget.set_server_status(MTM2.InnerLoopControlMode.Enabled, status=1, faults=0xFFFF)

    assert widget._labels["mode"].text() == "Enabled"
    assert widget._labels["status"].text() == "0x1"
    assert widget._labels["faults"].text() == "0xffff"

    assert widget._list_status_word["status"][0].palette().color(QPalette.Base) == Qt.red
    for indicator in widget._list_status_word["faults"]:
        assert indicator.palette().color(QPalette.Base) == Qt.red


def test_update_boolean_indicators(widget: TabIlc) -> None:
    status = 0x07
    widget._update_boolean_indicators(status, widget._list_status_word["status"])

    for idx, indicator in enumerate(widget._list_status_word["status"]):
        if status & (1 << idx):
            assert indicator.palette().color(QPalette.Base) == Qt.red
        else:
            assert indicator.palette().color(QPalette.Base) == Qt.gray


def test_set_scan_rate(widget: TabIlc) -> None:
    widget.set_scan_rate(5)

    assert widget._labels["rate"].text() == "240 (5)"

    widget.set_scan_rate(13)

    assert widget._labels["rate"].text() == "Unknown (13)"


def test_set_calibration_data(widget: TabIlc) -> None:
    widget.set_calibration_data(
        [1.0, 2.0, 3.0, 4.0],
        [2.0, 3.0, 4.0, 5.0],
        [3.0, 4.0, 5.0, 6.0],
        [4.0, 5.0, 6.0, 7.0],
        [5.0, 6.0, 7.0, 8.0],
        [6.0, 7.0, 8.0, 9.0],
    )

    for idx in range(widget.NUM_CHANNEL):
        assert widget._labels[f"main_gain_{idx + 1}"].text() == f"{float(idx + 1):.6e}"
        assert widget._labels[f"main_offset_{idx + 1}"].text() == f"{float(idx + 2):.5f}"
        assert widget._labels[f"main_sensitivity_{idx + 1}"].text() == f"{float(idx + 3):.5f}"

        assert widget._labels[f"backup_gain_{idx + 1}"].text() == f"{float(idx + 4):.6e}"
        assert widget._labels[f"backup_offset_{idx + 1}"].text() == f"{float(idx + 5):.5f}"
        assert widget._labels[f"backup_sensitivity_{idx + 1}"].text() == f"{float(idx + 6):.5f}"
