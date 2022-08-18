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

from lsst.ts.m2gui import Model, ActuatorForce
from lsst.ts.m2gui.controltab import TabDetailedForce


@pytest.fixture
def widget(qtbot):

    widget = TabDetailedForce("Detailed Force", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


async def test_callback_callback_hard_points(widget):

    axial = [1, 2, 3]
    tangent = [72, 73, 74]
    widget.model.utility_monitor.update_hard_points(axial, tangent)

    # Sleep one second to let the event loop to have the time to run the signal
    await asyncio.sleep(1)

    assert widget._hard_points["axial"].text() == str(axial)
    assert widget._hard_points["tangent"].text() == str(tangent)


async def test_callback_callback_forces(widget):

    forces = ActuatorForce()
    forces.f_hc[3] = 1.234
    forces.f_cur[5] = 0.2
    forces.f_error[7] = 0.249
    forces.encoder_count[10] = 123
    forces.step[13] = 34

    widget.model.utility_monitor.update_forces(forces)

    # Sleep one second to let the event loop to have the time to run the signal
    await asyncio.sleep(1)

    assert widget._forces["f_hc"][3].text() == "1.23"
    assert widget._forces["f_cur"][5].text() == "0.20"
    assert widget._forces["f_error"][7].text() == "0.25"
    assert widget._forces["encoder_count"][10].text() == "123"
    assert widget._forces["step"][13].text() == "34"
