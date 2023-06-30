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

import logging

import pytest
from lsst.ts.m2gui import Model
from lsst.ts.m2gui.controltab import TabRealtimeNetForceMoment
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> TabRealtimeNetForceMoment:
    widget = TabRealtimeNetForceMoment("Realtime Data", Model(logging.getLogger()))
    qtbot.addWidget(widget)

    return widget


@pytest.mark.asyncio
async def test_callback_time_out(widget: TabRealtimeNetForceMoment) -> None:
    for idx in range(len(widget.net_force_moment)):
        widget.net_force_moment[idx] = (idx + 1) * 0.1

    await widget._callback_time_out()

    for idx, figure in enumerate(widget._figures.values()):
        assert figure.get_points(0)[-1].y() == (idx + 1) * 0.1
