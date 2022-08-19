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

import asyncio
import logging
import pathlib

import pytest
from lsst.ts.m2gui import ActuatorForce, FigureActuatorData, Model
from lsst.ts.m2gui.controltab import TabCellStatus
from PySide2.QtCore import Qt

TIMEOUT = 1000


def get_cell_geometry_file():
    policy_dir = pathlib.Path(__file__).parents[0] / ".." / ".." / "policy"

    return policy_dir / "cell_geometry.yaml"


@pytest.fixture
def widget(qtbot):

    widget = TabCellStatus("Cell Status", Model(logging.getLogger()))
    widget.read_cell_geometry_file(get_cell_geometry_file())
    qtbot.addWidget(widget)

    return widget


def test_init(widget):

    mirror = widget._view_mirror

    assert mirror.mirror_radius == 1.780189734

    actuators = mirror.actuators

    assert len(actuators) == 78

    actuator_77 = actuators[76]
    assert actuator_77._acutator_id == 77
    assert actuator_77._alias == "A5"
    assert actuator_77.label_id.toPlainText() == "77"
    assert actuator_77._magnitude == 0


def text_callback_show_alias(qtbot, widget):

    qtbot.mouseClick(widget._button_show_alias, Qt.LeftButton)

    actuators = widget._view_mirror.actuators
    assert actuators[0].label_id.toPlainText() == "B1"


def test_get_data_selected(widget):

    # Update the internal holded force data
    widget._forces.f_cur[0] = 1

    data_selected, is_displacement = widget._get_data_selected()
    assert data_selected[0] == 1
    assert is_displacement is False


async def test_callback_selection_changed(widget):

    # Update the internal holded actuator data
    widget._forces.position_in_mm[0] = 3000
    widget._forces.position_in_mm[-1] = -3000

    widget._forces.f_error[0] = 2
    widget._forces.f_error[-1] = -2

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


async def test_callback_forces(qtbot, widget):

    actuator_force = ActuatorForce()
    actuator_force.f_cur[1] = 100
    actuator_force.f_error[1] = 72
    actuator_force.f_error[77] = -12

    widget.model.utility_monitor.update_forces(actuator_force)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._forces.f_cur[1] == 100
    assert widget._view_mirror.actuators[1]._magnitude == 100

    figure_realtime = widget._figures["realtime"]

    assert figure_realtime.get_series(0).count() == 1
    assert figure_realtime.get_series(1).count() == 1

    assert figure_realtime.get_points(0)[0].y() == 1
    assert figure_realtime.get_points(1)[0].y() == 2
