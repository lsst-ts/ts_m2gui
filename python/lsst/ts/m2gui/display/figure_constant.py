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

__all__ = ["FigureConstant"]

import numpy as np
from PySide6 import QtCharts
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QPainter


class FigureConstant(QtCharts.QChartView):
    """Figure to show the constant line data.

    This figure will allocate the memory space of the data points. The new
    data will update the existed points on figure directly. This means if you
    assign the "num_points" to be 10, you could not update the data to have >10
    data points with self.update_data().

    Parameters
    ----------
    range_x_min : `float` or `int`
        Minimum of the range of x-axis.
    range_x_max : `float` or `int`
        Maximum of the range of x-axis.
    num_points : `int`
        Number of the points.
    title_x : `str`
        Title of the x axis.
    title_y : `str`
        Title of the y axis.
    title_figure : `str`
        Title of the figure.
    legends : `list` [`str`]
        Legends. The number of elements should be the same as num_lines,
        otherwise, there will be the IndexError. Put [] if you do not want to
        show the legends.
    num_lines : `int`, optional
        Number of the lines. (the default is 1)
    is_realtime : `bool`, optional
        Is the realtime figure or not. (the default is False)

    Attributes
    ----------
    axis_x : `PySide6.QtCharts.QtCharts.QValueAxis`
        X axis.
    axis_y : `PySide6.QtCharts.QtCharts.QValueAxis`
        Y axis.
    """

    # Minimum width of the chart's view
    MINIMUM_WIDTH = 500

    # Offset of the y axis
    OFFSET_Y = 1

    def __init__(
        self,
        range_x_min: float | int,
        range_x_max: float | int,
        num_points: int,
        title_x: str,
        title_y: str,
        title_figure: str,
        legends: list[str],
        num_lines: int = 1,
        is_realtime: bool = False,
    ) -> None:
        super().__init__()

        self.axis_x = self._create_default_axis(range_x_min, range_x_max, title_x)
        self.axis_y = self._create_default_axis(-self.OFFSET_Y, self.OFFSET_Y, title_y)

        # Track the maximum and minimum y values in points. These are used to
        # decide the range of y-axis.
        self._value_y_min = 0.0
        self._value_y_max = 0.0

        self._num_points = num_points
        self._is_realtime = is_realtime

        # Counter of the realtime data
        self._counter_realtime = 0
        self._max_counter_realtime = num_points * num_lines

        self._set_chart(title_figure)

        self._set_default_series(range_x_min, range_x_max, num_lines, legends)

        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumWidth(self.MINIMUM_WIDTH)

    def _create_default_axis(
        self, range_min: float | int, range_max: float | int, title: str
    ) -> QtCharts.QValueAxis:
        """Create the default axis.

        Parameters
        ----------
        range_min : `float` or `int`
            Minimum of the range of x-axis.
        range_max : `float` or `int`
            Maximum of the range of x-axis.
        title : `str`
            Title of the axis.
        """

        axis = QtCharts.QValueAxis()
        axis.setRange(range_min, range_max)
        axis.setTitleText(title)

        return axis

    def _set_chart(self, title: str) -> None:
        """Set the chart.

        Parameters
        ----------
        title : `str`
            Title.
        """

        chart = QtCharts.QChart()
        chart.setTitle(title)
        chart.addAxis(self.axis_x, Qt.AlignBottom)
        chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.setChart(chart)

    def _set_default_series(
        self,
        range_x_min: float | int,
        range_x_max: float | int,
        num_lines: int,
        text_legends: list[str],
    ) -> None:
        """Set the default series.

        Parameters
        ----------
        range_x_min : `float` or `int`
            Minimum of the range of x-axis.
        range_x_max : `float` or `int`
            Maximum of the range of x-axis.
        num_lines : `int`
            Number of the lines.
        text_legends : `list` [`str`]
            Text of the legends. The number of elements should be the same as
            num_lines, otherwise, there will be the IndexError. Put [] if you
            do not want to show the legend.
        """

        chart = self.chart()

        is_set_legend = len(text_legends) != 0
        for idx in range(num_lines):
            series = QtCharts.QLineSeries()

            if is_set_legend:
                series.setName(text_legends[idx])

            if not self._is_realtime:
                # Default data to allocate the needed memory or space
                for x in np.linspace(range_x_min, range_x_max, num=self._num_points):
                    series.append(x, 0)

            chart.addSeries(series)

            series.attachAxis(self.axis_x)
            series.attachAxis(self.axis_y)

        if not is_set_legend:
            chart.legend().hide()

    def get_points(self, idx: int) -> list[QPointF]:
        """Get the points.

        Parameters
        ----------
        idx : `int`
            Index of the series.

        Returns
        -------
        `list` [`PySide6.QtCore.QPointF`]
            Points.
        """
        return self.get_series(idx).points()

    def get_series(self, idx: int) -> QtCharts.QLineSeries:
        """Get the series.

        Parameters
        ----------
        idx : `int`
            Index of the series.

        Returns
        -------
        `PySide6.QtCharts.QtCharts.QLineSeries`
            Series.
        """
        return self.chart().series()[idx]

    def update_data(self, list_x: list, list_y: list, idx: int = 0) -> None:
        """Update the data in figure.

        This can not be used for the realtime data.

        Parameters
        ----------
        list_x : `list`
            List of the x values.
        list_y : `list`
            List of the y values.
        idx : `int`, optional
            Index of the series. (the default is 0)

        Raises
        ------
        `RuntimeError`
            If the realtime data is applied.
        `ValueError`
            Input x number is more than the available points.
        """

        if self._is_realtime:
            raise RuntimeError("Cannot be called for the realtime data.")

        # Check the number of input data
        num_x = len(list_x)
        if num_x > self._num_points:
            raise ValueError(
                f"Input x number(={num_x}) > available points (={self._num_points})."
            )

        # Replace the points in series
        points = self.get_points(idx)
        for (
            point,
            x,
            y,
        ) in zip(points, list_x, list_y):
            point.setX(x)
            point.setY(y)

        series = self.get_series(idx)
        series.replace(points)

        # Check the range of y-axis needs to be updated or not
        self._value_y_min = min(self._value_y_min, *list_y)
        self._value_y_max = max(self._value_y_max, *list_y)
        self._update_range_axis_y()

    def _update_range_axis_y(self, threshold: float | int = 50) -> None:
        """Update the range of y-axis.

        This is used internally to track the incoming data and update the range
        only when required.

        Parameters
        ----------
        threshold : `float` or `int`, optional
            Threshold to decide the update of range. (the default is 50)
        """

        axis_max = self.axis_y.max()
        axis_min = self.axis_y.min()

        if (
            (self._value_y_min < axis_min)
            or (self._value_y_max > axis_max)
            or (abs(self._value_y_min - axis_min) > threshold)
            or (abs(self._value_y_max - axis_max) > threshold)
        ):
            self.axis_y.setRange(
                self._value_y_min - self.OFFSET_Y, self._value_y_max + self.OFFSET_Y
            )

    def adjust_range_axis_y(self, threshold: float | int = 1) -> None:
        """Adjust the range of y-axis.

        This is different from the self._update_range_axis_y(). Sometimes, it
        may be required to go through all the points to adjust the range of
        y-axis.

        Parameters
        ----------
        threshold : `float` or `int`, optional
            Threshold to decide the update of range. (the default is 1)
        """

        num_series = len(self.chart().series())

        values = list()
        for idx in range(num_series):
            value_min, value_max = self._get_range_points(idx)
            values.append(value_min)
            values.append(value_max)

        self._value_y_min = min(values)
        self._value_y_max = max(values)
        self._update_range_axis_y(threshold=threshold)

    def _get_range_points(self, idx: int) -> tuple[float, float]:
        """Get the range of points in a specific series.

        Parameters
        ----------
        idx : `int`
            Index of the series.

        Returns
        -------
        `float`
            Minimum value.
        `float`
            Maximum value.
        """

        points = self.get_points(idx)

        values = list()
        for point in points:
            values.append(point.y())

        return min(values), max(values)

    def append_data(self, value: float, idx: int = 0) -> None:
        """Append the data. This is only useful if the realtime data is
        applied.

        Parameters
        ----------
        value : `float`
            New coming data.
        idx : `int`, optional
            Index of the series. (the default is 0)

        Raises
        ------
        `RuntimeError`
            If not for the realtime data.
        """

        if not self._is_realtime:
            raise RuntimeError("Can only be called for the realtime data.")

        points = self.get_points(idx)
        self._append_point(points, value)

        # Replace the points in series
        series = self.get_series(idx)
        series.replace(points)

        # Update the range of axes to show the new data
        if self.axis_x.max() < points[-1].x():
            self.axis_x.setRange(points[0].x(), points[-1].x())

        # Check the range of y-axis needs to be updated or not
        self._value_y_max = max(self._value_y_max, value)
        self._value_y_min = min(self._value_y_min, value)
        self._update_range_axis_y()

        # Update the counter
        self._counter_realtime += 1
        if self._counter_realtime >= self._max_counter_realtime:
            self._counter_realtime = 0

            # Adjust the range of y-axis if needed
            self.adjust_range_axis_y(threshold=5)

    def _append_point(self, points: list[QPointF], value: float) -> None:
        """Append the point.

        Parameters
        ----------
        points : `list` [`PySide6.QtCore.QPointF`]
            Points.
        value : `float`
            New coming data.
        """

        length_points = len(points)

        # No data yet, begin from 0
        if length_points == 0:
            points.append(QPointF(0, value))

        # The holded amount of data is less than the allowed maximum. Add the
        # new point.
        elif length_points < self._num_points:
            points.append(QPointF(points[-1].x() + 1, value))

        # Pop the oldest point and append a new one.
        else:
            points.pop(0)
            points.append(QPointF(points[-1].x() + 1, value))
