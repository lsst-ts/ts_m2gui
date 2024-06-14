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
from lsst.ts.m2com import ActuatorDisplacementUnit
from lsst.ts.m2gui import ActuatorForceAxial, ActuatorForceTangent, LocalMode, Model
from lsst.ts.m2gui.controltab import TabActuatorControl
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabActuatorControl:
    widget = TabActuatorControl("Actuator Control", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest_asyncio.fixture
async def widget_async(qtbot: QtBot) -> TabActuatorControl:
    async with TabActuatorControl(
        "Actuator Control", Model(logging.getLogger(), is_simulation_mode=True)
    ) as widget_sim:
        qtbot.addWidget(widget_sim)

        await widget_sim.model.connect()
        yield widget_sim


def test_init(widget: TabActuatorControl) -> None:
    progress = widget._info_script["progress"]
    assert progress.minimum() == 0
    assert progress.maximum() == 100
    assert progress.value() == 0
    assert progress.isTextVisible() is True


@pytest.mark.asyncio
async def test_callback_script_load_script(widget_async: TabActuatorControl) -> None:
    await _transition_to_enable_state(widget_async)

    file_name = "/a/b/c"
    name = await widget_async._callback_script_load_script(file_name=file_name)

    assert name == "c"
    assert widget_async._info_script["file"].text() == file_name


async def _transition_to_enable_state(widget_async: TabActuatorControl) -> None:
    await widget_async.model.enter_diagnostic()
    await widget_async.model.enter_enable()


@pytest.mark.asyncio
async def test_callback_script_command(
    qtbot: QtBot, widget_async: TabActuatorControl
) -> None:
    await _transition_to_enable_state(widget_async)

    widget_async._callback_script_load_script(file_name="/a/b/c")
    widget_async.model.report_script_progress(30)

    qtbot.mouseClick(widget_async._buttons_script["clear"], Qt.LeftButton)

    assert widget_async._info_script["file"].text() == ""
    assert widget_async._info_script["progress"].value() == 0


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
    qtbot.mouseClick(
        widget._buttons_actuator_selection_support["select_ring"], Qt.LeftButton
    )

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
    qtbot.mouseClick(
        widget._buttons_actuator_selection_support["clear_all"], Qt.LeftButton
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._buttons_actuator_selection[idx].isChecked() is False


@pytest.mark.asyncio
async def test_callback_actuator_start(
    qtbot: QtBot, widget_async: TabActuatorControl
) -> None:
    # Transition to the enabled state with the open-loop control
    await _transition_to_enable_state(widget_async)

    controller = widget_async.model.controller
    await controller.switch_force_balance_system(False)

    # Select the actuators
    selected_actuators = [0, 1, 3, 7, 76, 77]
    for selected_actuator in selected_actuators:
        qtbot.mouseClick(
            widget_async._buttons_actuator_selection[selected_actuator], Qt.LeftButton
        )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    # Change the unit
    # Index begins from 0 instead of 1 in QComboBox
    index_step_unit = ActuatorDisplacementUnit.Step.value - 1
    widget_async._displacement_unit_selection.setCurrentIndex(index_step_unit)

    # Change the displacement
    widget_async._target_displacement.setValue(10)

    # Start the movement
    widget_async.model.local_mode = LocalMode.Enable
    (
        actuators,
        target_displacement,
        displacement_unit,
    ) = await widget_async._callback_actuator_start()

    assert actuators == selected_actuators
    assert target_displacement == widget_async._target_displacement.value()
    assert displacement_unit == ActuatorDisplacementUnit.Step

    # Sleep sometime to let the movement to be done
    await asyncio.sleep(10)


@pytest.mark.asyncio
async def test_callback_clear_force(
    qtbot: QtBot, widget_async: TabActuatorControl
) -> None:
    # Set the force
    widget_async._applied_force.setValue(10)

    # Clear the force
    await widget_async._callback_clear_force()

    assert widget_async._applied_force.value() == 0.0


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
