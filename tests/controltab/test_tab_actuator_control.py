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
import asyncio
import logging

from PySide2.QtCore import Qt

from lsst.ts.m2com import ActuatorDisplacementUnit

from lsst.ts.m2gui import Model, LocalMode, ActuatorForce
from lsst.ts.m2gui.controltab import TabActuatorControl


@pytest.fixture
def widget(qtbot):

    widget = TabActuatorControl("Actuator Control", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget):

    progress = widget._info_script["progress"]
    assert progress.minimum() == 0
    assert progress.maximum() == 100
    assert progress.value() == 0
    assert progress.isTextVisible() is True


async def test_callback_script_load_script(widget):

    widget.model.local_mode = LocalMode.Enable

    file_name = "/a/b/c"
    name = await widget._callback_script_load_script(file_name=file_name)

    assert name == "c"
    assert widget._info_script["file"].text() == file_name


def test_callback_script_command(qtbot, widget):

    widget.model.local_mode = LocalMode.Enable

    widget._callback_script_load_script(file_name="/a/b/c")
    widget.model.report_script_progress(30)

    qtbot.mouseClick(widget._buttons_script["clear"], Qt.LeftButton)

    assert widget._info_script["file"].text() == ""
    assert widget._info_script["progress"].value() == 0


def test_set_target_displacement(widget):

    widget._set_target_displacement(ActuatorDisplacementUnit.Millimeter)

    assert (
        widget._target_displacement.decimals()
        == widget.model.utility_monitor.NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT
    )
    assert widget._target_displacement.maximum() == widget.MAX_DISPLACEMENT_MM
    assert widget._target_displacement.minimum() == -widget.MAX_DISPLACEMENT_MM
    assert widget._target_displacement.suffix() == " mm"
    assert (
        widget._target_displacement.singleStep()
        == 10**-widget.model.utility_monitor.NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT
    )

    widget._set_target_displacement(ActuatorDisplacementUnit.Step)

    assert widget._target_displacement.decimals() == 0
    assert widget._target_displacement.maximum() == widget.MAX_DISPLACEMENT_STEP
    assert widget._target_displacement.minimum() == -widget.MAX_DISPLACEMENT_STEP
    assert widget._target_displacement.suffix() == " step"
    assert widget._target_displacement.singleStep() == 1


def test_set_target_displacement_exception(widget):

    with pytest.raises(ValueError):
        widget._set_target_displacement("Wrong Unit")


async def test_callback_selection_changed(widget):

    assert (
        widget._target_displacement.decimals()
        == widget.model.utility_monitor.NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT
    )

    # Index begins from 0 instead of 1 in QComboBox
    index_step_unit = ActuatorDisplacementUnit.Step.value - 1
    widget._displacement_unit_selection.setCurrentIndex(index_step_unit)

    # Sleep one second to let the event loop to have the time to run the signal
    await asyncio.sleep(1)

    assert widget._target_displacement.decimals() == 0


async def test_callback_select_ring(qtbot, widget):

    qtbot.mouseClick(
        widget._buttons_actuator_selection_support["select_ring"], Qt.LeftButton
    )

    # Sleep one second to let the event loop to have the time to run the signal
    await asyncio.sleep(1)

    for button in widget._buttons_actuator_selection:
        # The default selected ring is the ring B
        if button.text().startswith("B"):
            assert button.isChecked() is True
        else:
            assert button.isChecked() is False


async def test_callback_clear_all(qtbot, widget):

    # Select an actuator
    idx = 2
    qtbot.mouseClick(widget._buttons_actuator_selection[idx], Qt.LeftButton)

    # Sleep one second to let the event loop to have the time to run the signal
    await asyncio.sleep(1)

    assert widget._buttons_actuator_selection[idx].isChecked() is True

    # Clear the selection
    qtbot.mouseClick(
        widget._buttons_actuator_selection_support["clear_all"], Qt.LeftButton
    )

    # Sleep one second to let the event loop to have the time to run the signal
    await asyncio.sleep(1)

    assert widget._buttons_actuator_selection[idx].isChecked() is False


async def test_callback_actuator_start(qtbot, widget):

    # Select the actuators
    selected_actuators = [0, 1, 3, 7, 76, 77]
    for selected_actuator in selected_actuators:
        qtbot.mouseClick(
            widget._buttons_actuator_selection[selected_actuator], Qt.LeftButton
        )

    # Sleep one second to let the event loop to have the time to run the signal
    await asyncio.sleep(1)

    # Change the unit
    # Index begins from 0 instead of 1 in QComboBox
    index_step_unit = ActuatorDisplacementUnit.Step.value - 1
    widget._displacement_unit_selection.setCurrentIndex(index_step_unit)

    # Change the displacement
    widget._target_displacement.setValue(10)

    # Start the movement
    widget.model.local_mode = LocalMode.Enable
    (
        actuators,
        target_displacement,
        displacement_unit,
    ) = await widget._callback_actuator_start()

    assert actuators == selected_actuators
    assert target_displacement == widget._target_displacement.value()
    assert displacement_unit == ActuatorDisplacementUnit.Step


async def test_callback_progress(widget):

    progress = 20
    widget.model.report_script_progress(progress)

    # Sleep one second to let the event loop to have the time to run the signal
    await asyncio.sleep(1)

    assert widget._info_script["progress"].value() == progress


async def test_callback_forces(widget):

    actuator_force = ActuatorForce()
    actuator_force.f_cur[0] = -1
    actuator_force.f_cur[71] = 2
    actuator_force.f_cur[72] = 3
    actuator_force.f_cur[77] = -5

    widget.model.utility_monitor.update_forces(actuator_force)

    # Sleep one second to let the event loop to have the time to run the signal
    await asyncio.sleep(1)

    assert widget._labels_force["axial_min"].text() == "-1"
    assert widget._labels_force["axial_max"].text() == "2"
    assert widget._labels_force["axial_total"].text() == "1"

    assert widget._labels_force["tangent_min"].text() == "-5"
    assert widget._labels_force["tangent_max"].text() == "3"
    assert widget._labels_force["tangent_total"].text() == "-2"
