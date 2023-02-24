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
from lsst.ts.m2gui import Model
from lsst.ts.m2gui.controltab import TabConfigView


@pytest.fixture
def widget(qtbot):
    widget = TabConfigView("Configuration View", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_callback_signal_config(qtbot, widget):
    widget.model.report_config(
        file_configuration="a",
        file_version="b",
        file_control_parameters="c",
        file_lut_parameters="d",
        power_warning_motor=1.1,
        power_fault_motor=1.2,
        power_threshold_motor=1.3,
        power_warning_communication=1.4,
        power_fault_communication=1.5,
        power_threshold_communication=1.6,
        in_position_axial=1.7,
        in_position_tangent=1.8,
        in_position_sample=1.9,
        timeout_sal=2.1,
        timeout_crio=2.2,
        timeout_ilc=3.0,
        misc_range_angle=3.1,
        misc_diff_enabled=True,
        misc_range_temperature=3.2,
    )

    # Sleep so the event loop can access CPU to handle the signal
    await asyncio.sleep(1)

    assert widget._config_parameters["file_configuration"].text() == "a"
    assert widget._config_parameters["file_version"].text() == "b"
    assert widget._config_parameters["file_control_parameters"].text() == "c"
    assert widget._config_parameters["file_lut_parameters"].text() == "d"

    assert widget._config_parameters["power_warning_motor"].text() == "1.1 %"
    assert widget._config_parameters["power_fault_motor"].text() == "1.2 %"
    assert widget._config_parameters["power_threshold_motor"].text() == "1.3 A"

    assert widget._config_parameters["power_warning_communication"].text() == "1.4 %"
    assert widget._config_parameters["power_fault_communication"].text() == "1.5 %"
    assert widget._config_parameters["power_threshold_communication"].text() == "1.6 A"

    assert widget._config_parameters["in_position_axial"].text() == "1.7 N"
    assert widget._config_parameters["in_position_tangent"].text() == "1.8 N"
    assert widget._config_parameters["in_position_sample"].text() == "1.9 s"

    assert widget._config_parameters["timeout_sal"].text() == "2.1 s"
    assert widget._config_parameters["timeout_crio"].text() == "2.2 s"
    assert widget._config_parameters["timeout_ilc"].text() == "3 counts"

    assert widget._config_parameters["misc_range_angle"].text() == "3.1 degree"
    assert widget._config_parameters["misc_diff_enabled"].text() == "True"

    assert widget._config_parameters["misc_range_temperature"].text() == "3.2 degree C"
