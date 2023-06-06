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
import pathlib
from pathlib import Path

import pytest
from lsst.ts.m2com import NUM_ACTUATOR, NUM_TANGENT_LINK
from lsst.ts.m2gui import (
    ActuatorForceAxial,
    ActuatorForceTangent,
    CellActuatorGroupData,
    FigureActuatorData,
    Model,
)
from lsst.ts.m2gui.controltab import TabCellStatus
from lsst.ts.m2gui.display import ItemActuator
from PySide2.QtCore import Qt
from pytestqt.qtbot import QtBot

TIMEOUT = 1000


def get_cell_geometry_file() -> Path:
    policy_dir = pathlib.Path(__file__).parents[0] / ".." / ".." / "policy"

    return policy_dir / "cell_geometry.yaml"


@pytest.fixture
def widget(qtbot: QtBot) -> TabCellStatus:
    widget = TabCellStatus("Cell Status", Model(logging.getLogger()))
    widget.read_cell_geometry_file(get_cell_geometry_file())
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabCellStatus) -> None:
    mirror = widget._view_mirror

    assert mirror.mirror_radius == 1.780189734

    actuators = mirror.actuators

    assert len(actuators) == NUM_ACTUATOR

    actuator_77 = actuators[76]
    assert actuator_77.acutator_id == 77
    assert actuator_77._alias == "A5"
    assert actuator_77.label_id.toPlainText() == "77"
    assert actuator_77.magnitude == 0

    assert len(widget._visible_actuator_ids) == NUM_ACTUATOR


def text_callback_show_alias(qtbot: QtBot, widget: TabCellStatus) -> None:
    qtbot.mouseClick(widget._button_show_alias, Qt.LeftButton)

    actuators = widget._view_mirror.actuators
    assert actuators[0].label_id.toPlainText() == "B1"


@pytest.mark.asyncio
async def test_callback_selection_changed_group(widget: TabCellStatus) -> None:
    # Index begins from 0 instead of 1 in QComboBox
    index_group = CellActuatorGroupData.Tangent.value - 1
    widget._group_data_selector.setCurrentIndex(index_group)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    num = 0
    for actuator in widget._view_mirror.actuators:
        if actuator.isVisible():
            num += 1

    assert num == NUM_TANGENT_LINK


def test_get_visible_actuator_ids(widget: TabCellStatus) -> None:
    visible_actuators_all = widget.get_visible_actuator_ids(index_group_data_selector=0)
    assert len(visible_actuators_all) == NUM_ACTUATOR
    assert min(visible_actuators_all) == 1
    assert max(visible_actuators_all) == NUM_ACTUATOR

    visible_actuators_axial = widget.get_visible_actuator_ids(
        index_group_data_selector=1
    )

    num_actuators_axial = NUM_ACTUATOR - NUM_TANGENT_LINK
    assert len(visible_actuators_axial) == num_actuators_axial
    assert min(visible_actuators_axial) == 1
    assert max(visible_actuators_axial) == num_actuators_axial

    visible_actuators_tangent = widget.get_visible_actuator_ids(
        index_group_data_selector=2
    )
    assert len(visible_actuators_tangent) == NUM_TANGENT_LINK
    assert min(visible_actuators_tangent) == num_actuators_axial + 1
    assert max(visible_actuators_tangent) == NUM_ACTUATOR


def test_get_data_selected(widget: TabCellStatus) -> None:
    # Update the internal holded force data
    widget._forces_axial.f_cur[0] = 1

    data_selected, is_displacement = widget._get_data_selected()
    assert data_selected[0] == 1
    assert is_displacement is False


@pytest.mark.asyncio
async def test_callback_selection_changed(widget: TabCellStatus) -> None:
    # Update the internal holded actuator data
    widget._forces_axial.position_in_mm[0] = 3000
    widget._forces_tangent.position_in_mm[-1] = -3000

    widget._forces_axial.f_error[0] = 2
    widget._forces_tangent.f_error[-1] = -2

    # Displacement

    # Index begins from 0 instead of 1 in QComboBox
    index_actuator_data = FigureActuatorData.Displacement.value - 1
    widget._actuator_data_selection.setCurrentIndex(index_actuator_data)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._figures["axial"].axis_y.titleText() == "Position (mm)"
    assert widget._figures["tangent"].axis_y.titleText() == "Position (mm)"

    assert widget._figures["axial"].get_points(0)[0].y() == 3000
    assert widget._figures["tangent"].get_points(0)[-1].y() == -3000

    assert widget._figures["axial"].axis_y.min() == -1
    assert widget._figures["axial"].axis_y.max() == 3001

    assert widget._figures["tangent"].axis_y.min() == -3001
    assert widget._figures["tangent"].axis_y.max() == 1

    # Force

    index_actuator_data = FigureActuatorData.ForceError.value - 1
    widget._actuator_data_selection.setCurrentIndex(index_actuator_data)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._figures["axial"].axis_y.titleText() == "Force (N)"
    assert widget._figures["tangent"].axis_y.titleText() == "Force (N)"

    assert widget._figures["axial"].get_points(0)[0].y() == 2
    assert widget._figures["tangent"].get_points(0)[-1].y() == -2

    assert widget._figures["axial"].axis_y.min() == -1
    assert widget._figures["axial"].axis_y.max() == 3

    assert widget._figures["tangent"].axis_y.min() == -3
    assert widget._figures["tangent"].axis_y.max() == 1


@pytest.mark.asyncio
async def test_callback_time_out(widget: TabCellStatus) -> None:
    # Select the actuator
    for item in widget._view_mirror.items():
        if isinstance(item, ItemActuator):
            if item.label_id.toPlainText() == "2":
                item.setSelected(True)

    widget._forces_axial.f_cur[1] = 100
    widget._forces_axial.f_error[1] = 72
    widget._forces_tangent.f_error[-1] = -12
    await widget._callback_time_out()

    assert widget._forces_axial.f_cur[1] == 100
    assert widget._view_mirror.actuators[1].magnitude == 100

    figure_realtime = widget._figures["realtime"]

    assert figure_realtime.get_series(0).count() > 0
    assert figure_realtime.get_series(1).count() > 0

    assert figure_realtime.get_points(0)[-1].y() == 1
    assert figure_realtime.get_points(1)[-1].y() == 2

    text_force = widget._view_mirror.get_text_force()
    assert text_force.toPlainText() == "Actuator Force:\nID: 2, force: 100 N"


@pytest.mark.asyncio
async def test_callback_forces_axial(widget: TabCellStatus) -> None:
    actuator_force = ActuatorForceAxial()
    actuator_force.f_cur[1] = 100

    widget.model.utility_monitor.update_forces_axial(actuator_force)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert id(widget._forces_axial) == id(actuator_force)


@pytest.mark.asyncio
async def test_callback_forces_tangent(widget: TabCellStatus) -> None:
    actuator_force = ActuatorForceTangent()
    actuator_force.f_cur[1] = 100

    widget.model.utility_monitor.update_forces_tangent(actuator_force)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert id(widget._forces_tangent) == id(actuator_force)
