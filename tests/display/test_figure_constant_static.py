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
from lsst.ts.m2gui.display import FigureConstant
from pytestqt.qtbot import QtBot


@pytest.fixture
def widget(qtbot: QtBot) -> FigureConstant:
    widget = FigureConstant(
        2,
        5,
        10,
        "title_x",
        "title_y",
        "title_figure",
        ["text_legend_1", "text_legend_2"],
        num_lines=2,
    )
    qtbot.addWidget(widget)

    return widget


def test_init(widget: FigureConstant) -> None:
    assert widget.axis_x.min() == 2
    assert widget.axis_x.max() == 5

    assert widget.axis_y.min() == -widget.OFFSET_Y
    assert widget.axis_y.max() == widget.OFFSET_Y

    assert widget.axis_x.titleText() == "title_x"
    assert widget.axis_y.titleText() == "title_y"

    assert widget.chart().title() == "title_figure"

    markers = widget.chart().legend().markers()
    assert markers[0].label() == "text_legend_1"
    assert markers[1].label() == "text_legend_2"


def test_get_points(widget: FigureConstant) -> None:
    for idx in range(0, 2):
        points = widget.get_points(0)
        for point in points:
            assert point.y() == 0

        assert points[0].x() == 2
        assert points[-1].x() == 5


def test_get_series(widget: FigureConstant) -> None:
    for idx in range(0, 2):
        series = widget.get_series(idx)
        assert series.count() == 10


def test_update_range_axis_y(widget: FigureConstant) -> None:
    # The new minimum is smaller than the axis
    widget._value_y_min = -100
    widget._update_range_axis_y()

    assert widget.axis_y.min() == -101
    assert widget.axis_y.max() == 1

    # The new maximum is bigger than the axis
    widget._value_y_max = 100
    widget._update_range_axis_y()

    assert widget.axis_y.min() == -101
    assert widget.axis_y.max() == 101

    # The "minimum" difference between the axis and values are big
    widget._value_y_min = -10
    widget._update_range_axis_y()

    assert widget.axis_y.min() == -11
    assert widget.axis_y.max() == 101

    # The "maximum" difference between the axis and values are big
    widget._value_y_max = 10
    widget._update_range_axis_y()

    assert widget.axis_y.min() == -11
    assert widget.axis_y.max() == 11


def test_update_data_exception(widget: FigureConstant) -> None:
    data = range(0, 12)

    with pytest.raises(ValueError):
        widget.update_data(data, data)


def test_update_data(widget: FigureConstant) -> None:
    # Update the first series
    data_x = range(2, 12)
    data_y_0 = range(3, 13)
    widget.update_data(data_x, data_y_0, idx=0)

    for point, x, y in zip(widget.get_points(0), data_x, data_y_0):
        assert point.x() == x
        assert point.y() == y

    assert widget.axis_y.min() == -1
    assert widget.axis_y.max() == 13

    # Update the second series
    data_y_1 = range(-8, 2)
    widget.update_data(data_x, data_y_1, idx=1)

    for point, x, y in zip(widget.get_points(1), data_x, data_y_1):
        assert point.x() == x
        assert point.y() == y

    assert widget.axis_y.min() == -9
    assert widget.axis_y.max() == 13


def test_adjust_range_axis_y(widget: FigureConstant) -> None:
    data_x = range(2, 12)
    data_y_0 = range(3, 13)
    widget.update_data(data_x, data_y_0, idx=0)

    data_y_1 = range(-13, -3)
    widget.update_data(data_x, data_y_1, idx=1)

    widget.adjust_range_axis_y()

    assert widget._value_y_min == -13
    assert widget._value_y_max == 12

    assert widget.axis_y.min() == -14
    assert widget.axis_y.max() == 13


def test_get_range_points(widget: FigureConstant) -> None:
    data_x = range(2, 12)
    data_y = range(3, 13)
    widget.update_data(data_x, data_y, idx=0)

    value_min, value_max = widget._get_range_points(0)

    assert value_min == min(data_y)
    assert value_max == max(data_y)


def test_append_data_exception(widget: FigureConstant) -> None:
    with pytest.raises(RuntimeError):
        widget.append_data(1)
