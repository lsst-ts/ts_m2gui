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
from lsst.ts import salobj
from lsst.ts.m2com import PowerType
from lsst.ts.m2gui import DisplacementSensorDirection, Model, TemperatureGroup
from lsst.ts.m2gui.controltab import TabUtilityView
from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette


@pytest.fixture
def widget(qtbot):

    widget = TabUtilityView("Utility View", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest_asyncio.fixture
async def widget_async(qtbot):
    async with TabUtilityView(
        "Utility View", Model(logging.getLogger(), is_simulation_mode=True)
    ) as widget_sim:
        qtbot.addWidget(widget_sim)

        await widget_sim.model.connect()
        yield widget_sim


def test_init(widget):

    for breaker in widget._breakers.keys():
        palette = widget._breakers[breaker].palette()
        color = palette.color(QPalette.Button)
        assert color == Qt.gray


@pytest.mark.asyncio
async def test_callback_reset_breakers(widget_async):

    # Transition to Disabled state to turn on the communication power
    await widget_async.model.controller.write_command_to_server(
        "start", controller_state_expected=salobj.State.DISABLED
    )

    name = "J3-W14-2"
    widget_async.model.utility_monitor.update_breaker(name, True)

    await widget_async._callback_reset_breakers(PowerType.Communication)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(8)

    palette = widget_async._breakers[name].palette()
    color = palette.color(QPalette.Button)
    assert color == Qt.green


@pytest.mark.asyncio
async def test_callback_power_motor(qtbot, widget):

    widget.model.utility_monitor.update_power_calibrated(PowerType.Motor, 0.1, 0.2)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._power_inclinometer["power_voltage_motor"].text() == "0.1 V"
    assert widget._power_inclinometer["power_current_motor"].text() == "0.2 A"


@pytest.mark.asyncio
async def test_callback_power_communication(qtbot, widget):

    widget.model.utility_monitor.update_power_calibrated(
        PowerType.Communication, 0.1, 0.2
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._power_inclinometer["power_voltage_communication"].text() == "0.1 V"
    assert widget._power_inclinometer["power_current_communication"].text() == "0.2 A"


@pytest.mark.asyncio
async def test_callback_inclinometer(widget):

    widget.model.utility_monitor.update_inclinometer_angle(
        0.1, new_angle_processed=0.55
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._power_inclinometer["inclinometer_raw"].text() == "0.1 degree"
    assert widget._power_inclinometer["inclinometer_processed"].text() == "0.6 degree"


@pytest.mark.asyncio
async def test_callback_inclinometer_tma(widget):

    widget.model.utility_monitor.update_inclinometer_angle(0.1, is_internal=False)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._power_inclinometer["inclinometer_tma"].text() == "0.1 degree"


@pytest.mark.asyncio
async def test_callback_breakers(qtbot, widget):

    name = "J1-W9-3"
    widget.model.utility_monitor.update_breaker(name, True)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    palette = widget._breakers[name].palette()
    color = palette.color(QPalette.Button)
    assert color == Qt.green


@pytest.mark.asyncio
async def test_callback_temperatures(qtbot, widget):

    temperature_group = TemperatureGroup.LG3
    temperatures = list(range(1, 5))

    utility_monitor = widget.model.utility_monitor
    utility_monitor.update_temperature(temperature_group, temperatures)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    sensors = utility_monitor.get_temperature_sensors(temperature_group)
    for sensor, temperature in zip(sensors, temperatures):
        assert widget._temperatures[sensor].text() == f"{temperature} degree C"


@pytest.mark.asyncio
async def test_callback_displacements(qtbot, widget):

    direction = DisplacementSensorDirection.Delta
    displacements = list(range(1, 7))

    utility_monitor = widget.model.utility_monitor
    utility_monitor.update_displacements(direction, displacements)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    sensors = utility_monitor.get_displacement_sensors(direction)
    for sensor, displacement in zip(sensors, displacements):
        assert widget._displacements[sensor].text() == f"{displacement} mm"
