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
from lsst.ts.m2gui import ActuatorForceAxial, ActuatorForceTangent, Model
from lsst.ts.m2gui.controltab import TabDetailedForce
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabDetailedForce:
    widget = TabDetailedForce("Detailed Force", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_callback_time_out(widget: TabDetailedForce) -> None:
    # Check the axial actuators
    widget._forces_latest_axial.f_hc[3] = 1.234
    widget._forces_latest_axial.f_cur[5] = 0.2
    widget._forces_latest_axial.f_error[7] = 0.249
    widget._forces_latest_axial.position_in_mm[10] = 123
    widget._forces_latest_axial.step[13] = 34
    await widget._callback_time_out()

    assert widget._forces["f_hc"][3].text() == "1.23"
    assert widget._forces["f_cur"][5].text() == "0.20"
    assert widget._forces["f_error"][7].text() == "0.25"
    assert widget._forces["position_in_mm"][10].text() == "123.0000"
    assert widget._forces["step"][13].text() == "34"

    # Check the tangent links
    widget._forces_latest_tangent.f_hc[0] = 1.234
    widget._forces_latest_tangent.f_cur[1] = 0.2
    widget._forces_latest_tangent.f_error[2] = 0.249
    widget._forces_latest_tangent.position_in_mm[3] = 123
    widget._forces_latest_tangent.step[4] = 34
    await widget._callback_time_out()

    assert widget._forces["f_hc"][72].text() == "1.23"
    assert widget._forces["f_cur"][73].text() == "0.20"
    assert widget._forces["f_error"][74].text() == "0.25"
    assert widget._forces["position_in_mm"][75].text() == "123.0000"
    assert widget._forces["step"][76].text() == "34"


@pytest.mark.asyncio
async def test_callback_hard_points(widget: TabDetailedForce) -> None:
    axial = [1, 2, 3]
    tangent = [72, 73, 74]
    widget.model.utility_monitor.update_hard_points(axial, tangent)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._hard_points["axial"].text() == str(axial)
    assert widget._hard_points["tangent"].text() == str(tangent)


@pytest.mark.asyncio
async def test_callback_forces_axial(widget: TabDetailedForce) -> None:
    forces = ActuatorForceAxial()
    forces.f_cur[5] = 0.2
    widget.model.utility_monitor.update_forces_axial(forces)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert id(widget._forces_latest_axial) == id(forces)


@pytest.mark.asyncio
async def test_callback_forces_tangent(widget: TabDetailedForce) -> None:
    forces = ActuatorForceTangent()
    forces.f_cur[3] = 0.2
    widget.model.utility_monitor.update_forces_tangent(forces)

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert id(widget._forces_latest_tangent) == id(forces)
