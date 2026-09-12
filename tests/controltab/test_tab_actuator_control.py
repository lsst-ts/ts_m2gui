# This file is part of ts_m2gui.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import asyncio
import logging

import pytest
import pytest_asyncio
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from lsst.ts.m2com import ActuatorDisplacementUnit
from lsst.ts.m2gui import ActuatorForceAxial, ActuatorForceTangent, Model
from lsst.ts.m2gui.controltab import TabActuatorControl


@pytest_asyncio.fixture
def widget(qtbot: QtBot) -> TabActuatorControl:
    widget = TabActuatorControl("Actuator Control", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


def test_init(widget: TabActuatorControl) -> None:
    progress = widget._info_script["progress"]
    assert progress.minimum() == 0
    assert progress.maximum() == 100
    assert progress.value() == 0
    assert progress.isTextVisible() is True


@pytest.mark.asyncio
async def test_callback_script_load_script(widget: TabActuatorControl) -> None:
    file_name = "/a/b/c"
    name = await widget._callback_script_load_script(file_name=file_name, bypass_load=True)

    assert name == "c"
    assert widget._info_script["file"].text() == file_name


@pytest.mark.asyncio
async def test_callback_script_command(qtbot: QtBot, widget: TabActuatorControl) -> None:
    widget._callback_script_load_script(file_name="/a/b/c", bypass_load=True)
    widget.model.report_script_progress(30)

    qtbot.mouseClick(widget._buttons_script["clear"], Qt.LeftButton)

    assert widget._info_script["file"].text() == ""
    assert widget._info_script["progress"].value() == 0


def test_set_target_displacement(widget: TabActuatorControl) -> None:
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


def test_set_target_displacement_exception(widget: TabActuatorControl) -> None:
    with pytest.raises(ValueError):
        widget._set_target_displacement("Wrong Unit")


@pytest.mark.asyncio
async def test_callback_selection_changed(widget: TabActuatorControl) -> None:
    assert (
        widget._target_displacement.decimals()
        == widget.model.utility_monitor.NUM_DIGIT_AFTER_DECIMAL_DISPLACEMENT
    )

    # Index begins from 0 instead of 1 in QComboBox
    index_step_unit = ActuatorDisplacementUnit.Step.value - 1
    widget._displacement_unit_selection.setCurrentIndex(index_step_unit)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._target_displacement.decimals() == 0


@pytest.mark.asyncio
async def test_callback_select_ring(qtbot: QtBot, widget: TabActuatorControl) -> None:
    qtbot.mouseClick(widget._buttons_actuator_selection_support["select_ring"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    for button in widget._buttons_actuator_selection:
        # The default selected ring is the ring B
        if button.text().startswith("B"):
            assert button.isChecked() is True
        else:
            assert button.isChecked() is False


@pytest.mark.asyncio
async def test_callback_clear_all(qtbot: QtBot, widget: TabActuatorControl) -> None:
    # Select an actuator
    idx = 2
    qtbot.mouseClick(widget._buttons_actuator_selection[idx], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._buttons_actuator_selection[idx].isChecked() is True

    # Clear the selection
    qtbot.mouseClick(widget._buttons_actuator_selection_support["clear_all"], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._buttons_actuator_selection[idx].isChecked() is False


@pytest.mark.asyncio
async def test_get_selected_actuators_and_displacement_and_unit(
    qtbot: QtBot, widget: TabActuatorControl
) -> None:
    # Select the actuators
    selected_actuators = [0, 1, 3, 7, 76, 77]
    for selected_actuator in selected_actuators:
        qtbot.mouseClick(widget._buttons_actuator_selection[selected_actuator], Qt.LeftButton)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    # Change the unit
    # Index begins from 0 instead of 1 in QComboBox
    index_step_unit = ActuatorDisplacementUnit.Step.value - 1
    widget._displacement_unit_selection.setCurrentIndex(index_step_unit)

    # Change the displacement
    widget._target_displacement.setValue(10)

    # Get the movement details
    (
        actuators,
        target_displacement,
        displacement_unit,
    ) = widget._get_selected_actuators_and_displacement_and_unit()

    assert actuators == selected_actuators
    assert target_displacement == widget._target_displacement.value()
    assert displacement_unit == ActuatorDisplacementUnit.Step


@pytest.mark.asyncio
async def test_clear_applied_force(widget: TabActuatorControl) -> None:
    # Set the force
    widget._applied_force.setValue(10)

    # Clear the force
    widget._clear_applied_force()

    assert widget._applied_force.value() == 0.0


@pytest.mark.asyncio
async def test_callback_progress(widget: TabActuatorControl) -> None:
    progress = 20
    widget.model.report_script_progress(progress)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._info_script["progress"].value() == progress


@pytest.mark.asyncio
async def test_callback_forces_axial(widget: TabActuatorControl) -> None:
    actuator_force = ActuatorForceAxial()
    actuator_force.f_cur[0] = -1
    actuator_force.f_cur[71] = 2

    widget.model.utility_monitor.update_forces_axial(actuator_force)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._labels_force["axial_min"].text() == "-1.00"
    assert widget._labels_force["axial_max"].text() == "2.00"
    assert widget._labels_force["axial_total"].text() == "1.00"


@pytest.mark.asyncio
async def test_callback_forces_tangent(widget: TabActuatorControl) -> None:
    actuator_force = ActuatorForceTangent()
    actuator_force.f_cur[0] = 3
    actuator_force.f_cur[5] = -5

    widget.model.utility_monitor.update_forces_tangent(actuator_force)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._labels_force["tangent_min"].text() == "-5.00"
    assert widget._labels_force["tangent_max"].text() == "3.00"
    assert widget._labels_force["tangent_total"].text() == "-2.00"
