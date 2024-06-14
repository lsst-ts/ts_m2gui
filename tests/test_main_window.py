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

import pytest
from lsst.ts.m2com import get_config_dir, read_yaml_file
from lsst.ts.m2gui import MainWindow
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolBar
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> MainWindow:
    widget = MainWindow(False, False, False, log_level=13)
    qtbot.addWidget(widget)

    return widget


@pytest.fixture
def widget_sim(qtbot: QtBot) -> MainWindow:
    widget_sim = MainWindow(False, False, True)
    qtbot.addWidget(widget_sim)

    return widget_sim


def test_init(widget: MainWindow) -> None:
    assert widget.log.level == 13

    tool_bar = widget.findChildren(QToolBar)[0]
    actions = tool_bar.actions()

    assert len(actions) == 4

    controller = widget.model.controller
    configuration = _get_config()
    assert controller.host == configuration["host"]
    assert controller.port_command == configuration["port_command"]
    assert controller.port_telemetry == configuration["port_telemetry"]
    assert controller.timeout_connection == configuration["timeout_connection"]


def _get_config() -> dict:
    filepath = get_config_dir() / "default_gui.yaml"
    return read_yaml_file(filepath)


def test_set_model(widget: MainWindow) -> None:
    model_local_host = widget._set_model(True, False)
    assert model_local_host.controller.host == "127.0.0.1"

    model_crio_simulator = widget._set_model(False, True)
    assert model_crio_simulator.controller.host == _get_config()["host_crio_simulator"]

    with pytest.raises(ValueError):
        widget._set_model(True, True)


def test_init_sim(widget_sim: MainWindow) -> None:
    assert widget_sim.model.controller.host == "127.0.0.1"


def test_get_action(widget: MainWindow) -> None:
    button_exit = widget._get_action("Exit")
    assert button_exit.text() == "Exit"

    button_wrong_action = widget._get_action("WrongAction")
    assert button_wrong_action is None


@pytest.mark.asyncio
async def test_callback_settings(qtbot: QtBot, widget: MainWindow) -> None:
    assert widget._tab_settings.isVisible() is False

    button_settings = widget._get_action("Settings")
    qtbot.mouseClick(button_settings, Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._tab_settings.isVisible() is True
