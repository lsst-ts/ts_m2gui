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

__all__ = ["Gauge"]

from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QColor, QPainter, QPaintEvent
from PySide2.QtWidgets import QWidget


class Gauge(QWidget):
    """Draws gauge with the color scale.

    Parameters
    ----------
    magnitude_min : `float` or `int`
        Minimal magnitude in gauge.
    magnitude_max : `float` or `int`
        Maximal magnitude in gauge.

    Attributes
    ----------
    min : `float` or `int`
        Minimum of the gauge.
    max : `float` or `int`
        Maximum of the gauge.
    """

    # Minimum size of widget
    MIN_SIZE = 100

    def __init__(self, magnitude_min: float | int, magnitude_max: float | int) -> None:
        super().__init__()

        # These two new attributes decide the color range in this class. The
        # following self.set_magnitude_range() will check the inputs are
        # reasonable or not.
        self.min = 0.0
        self.max = 0.0
        self.set_magnitude_range(magnitude_min, magnitude_max)

        self.setMinimumSize(self.MIN_SIZE, self.MIN_SIZE)
        self.setMaximumWidth(2 * self.MIN_SIZE)

    def set_magnitude_range(
        self, magnitude_min: float | int, magnitude_max: float | int
    ) -> None:
        """Set the magnitude range. Color is mapped between magnitude_min and
        magnitude_max.

        Parameters
        ----------
        magnitude_min : `float` or `int`
            Minimal magnitude in gauge.
        magnitude_max : `float` or `int`
            Maximal magnitude in gauge.

        Raises
        ------
        `ValueError`
            If minimum magnitude >= maximum magnitude.
        """

        if magnitude_min >= magnitude_max:
            raise ValueError("Minimum magnitude should be less than maximum magnitude.")

        self.min = magnitude_min
        self.max = magnitude_max

        self.update()

    def sizeHint(self) -> QSize:
        """Overridden method. This is to provide the hint of size."""
        return QSize(self.MIN_SIZE, self.MIN_SIZE)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Overridden method. Paint gauge as series of lines, and add text
        labels.

        Parameters
        ----------
        event : `PySide2.QtGui.QPaintEvent`
            Paint event.
        """

        height = self.height()

        min_width = 20
        width = max(self.width() - self.MIN_SIZE, min_width)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        for x in range(0, height):
            magnitude = (height - x) / height
            painter.setPen(Gauge.get_color(magnitude))
            painter.drawLine(0, x, width, x)

        # Put the text of range
        painter.setPen(Qt.black)

        offset = 20
        format_text = "{0:.2f}"
        painter.drawText(
            0,
            0,
            self.width() - width,
            offset,
            Qt.AlignCenter,
            format_text.format(self.max),
        )

        painter.drawText(
            0,
            height - offset,
            self.width() - width,
            offset,
            Qt.AlignCenter,
            format_text.format(self.min),
        )

    @staticmethod
    def get_color(magnitude: float) -> QColor:
        """Get the color.

        Mimic the following colorbar as the default one in MATLAB:
        https://www.mathworks.com/help/matlab/ref/colorbar.html

        Parameters
        ----------
        magnitude : `float`
            Magnitude. This value should be between [0, 1]. If the magnitude is
            1, the color will be yellow. If the magniture is 0, the color will
            be blue.

        Returns
        -------
        `PySide2.QtGui.QColor`
            Color.
        """

        # For the hue in HSV model, the yellow is 60 degree and the blue is 240
        # degree. Put the yellow as the strongest magnitude and blue as the
        # weakest magnitude.
        hue_blue = 2 / 3
        difference_yellow_blue = 0.5
        hue = hue_blue - difference_yellow_blue * magnitude
        return QColor.fromHsvF(hue, 1, 1)
