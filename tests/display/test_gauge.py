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

import pytest
from lsst.ts.m2gui.display import Gauge


@pytest.fixture
def widget(qtbot):

    widget = Gauge(1, 2)
    qtbot.addWidget(widget)

    return widget


def test_init(widget):

    assert widget.min == 1
    assert widget.max == 2


def test_set_magnitude_exception(widget):

    with pytest.raises(ValueError):
        widget.set_magnitude_range(2, 1)

    with pytest.raises(ValueError):
        widget.set_magnitude_range(1, 1)


def test_set_magnitude_range(widget):

    widget.set_magnitude_range(-3, 4)

    assert widget.min == -3
    assert widget.max == 4


def test_get_color():

    # For the yellow color, the hue is 60 degree in HSV model
    color_yellow = Gauge.get_color(1)

    assert color_yellow.hue() == 60

    # For the blue color, the hue is 240 degree in HSV model
    color_blue = Gauge.get_color(0)

    assert color_blue.hue() == 240
