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

__all__ = ["FigureConstant"]

import numpy as np

from PySide2.QtCore import Qt, QPointF
from PySide2.QtCharts import QtCharts
from PySide2.QtGui import QPainter


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

    Attributes
    ----------
    axis_x : `PySide2.QtCharts.QtCharts.QValueAxis`
        X axis.
    axis_y : `PySide2.QtCharts.QtCharts.QValueAxis`
        Y axis.
    """

    # Minimum width of the chart's view
    MINIMUM_WIDTH = 500

    # Offset of the y axis
    OFFSET_Y = 1

    def __init__(
        self, range_x_min, range_x_max, num_points, title_x, title_y, title_figure
    ):
        super().__init__()

        self.axis_x = self._create_default_axis(range_x_min, range_x_max, title_x)
        self.axis_y = self._create_default_axis(-self.OFFSET_Y, self.OFFSET_Y, title_y)

        self._set_chart(title_figure)

        self._set_default_series(range_x_min, range_x_max, num_points)

        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumWidth(self.MINIMUM_WIDTH)

    def _create_default_axis(self, range_min, range_max, title):
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

    def _set_chart(self, title):
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

    def _set_default_series(self, range_x_min, range_x_max, num_points):
        """Set the default series.

        Parameters
        ----------
        range_x_min : `float` or `int`
            Minimum of the range of x-axis.
        range_x_max : `float` or `int`
            Maximum of the range of x-axis.
        num_points : `int`
            Number of the points.
        """

        # Default data to allocate the needed memory or space
        series = QtCharts.QLineSeries()
        for x in np.linspace(range_x_min, range_x_max, num=num_points):
            series.append(x, 0)

        chart = self.chart()
        chart.addSeries(series)

        series.attachAxis(self.axis_x)
        series.attachAxis(self.axis_y)

    def update_data(self, list_x, list_y):
        """Update the data in figure.

        Parameters
        ----------
        list_x : `list`
            List of the x values.
        list_y : `list`
            List of the y values.

        Raises
        ------
        `ValueError`
            Input x number is more than the available points.
        """

        num_x = len(list_x)

        series = self.chart().series()[0]
        count = series.count()
        if num_x > count:
            raise ValueError(f"Input x number(={num_x}) > available points (={count}).")

        points = [QPointF(x, y) for (x, y) in zip(list_x, list_y)]
        series.replace(points)

        self.axis_y.setRange(min(list_y) - self.OFFSET_Y, max(list_y) + self.OFFSET_Y)
