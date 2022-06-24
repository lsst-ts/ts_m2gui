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

from lsst.ts.m2gui.display import Figure


@pytest.fixture
def widget(qtbot):

    widget = Figure(2, 5, 10, "title_x", "title_y", "title_figure")
    qtbot.addWidget(widget)

    return widget


def test_init(widget):

    assert widget.axis_x.min() == 2
    assert widget.axis_x.max() == 5

    assert widget.axis_y.min() == -widget.OFFSET_Y
    assert widget.axis_y.max() == widget.OFFSET_Y

    assert widget._series.count() == 10

    assert widget.axis_x.titleText() == "title_x"
    assert widget.axis_y.titleText() == "title_y"

    assert widget._chart.title() == "title_figure"


def test_update_data_exception(widget):

    data = range(0, 12)

    with pytest.raises(ValueError):
        widget.update_data(data, data)


def test_update_data(widget):

    data_x = range(2, 12)
    data_y = range(3, 13)
    widget.update_data(data_x, data_y)

    for point, x, y in zip(widget._series.points(), data_x, data_y):
        assert point.x() == x
        assert point.y() == y

    assert widget.axis_y.min() == min(data_y) - widget.OFFSET_Y
    assert widget.axis_y.max() == max(data_y) + widget.OFFSET_Y
