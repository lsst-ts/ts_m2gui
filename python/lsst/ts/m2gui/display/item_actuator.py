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

__all__ = ["ItemActuator"]

from PySide2.QtCore import Qt
from PySide2.QtGui import QPen
from PySide2.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem

from . import Gauge


class ItemActuator(QGraphicsEllipseItem):
    """Actuator item used in the ViewMirror class to show the actuator
    information.

    Parameters
    ----------
    x : `float`
        Actuator x position on the mirror's view.
    y : `float`
        Actuator y position on the mirror's view.
    diameter : `float` or `int`
        Diameter of the actuator on the mirror's view.
    actuator_id : `int`
        Actuator ID.
    alias : `str`
        Alias of the actuator.
    point_size : `int`
        Point size of the text.

    Attributes
    ----------
    label_id : `PySide2.QtWidgets.QGraphicsTextItem`
        Label of the actuator ID.
    """

    def __init__(self, x, y, diameter, actuator_id, alias, point_size):
        super().__init__(x, y, diameter, diameter)

        self._acutator_id = actuator_id
        self._alias = alias

        # Magnitude to to decide the color of actuator on the mirror's view
        self._magnitude = 0

        # Note that the ItemActuator class will become the parent of
        # self.label_id
        self.label_id = QGraphicsTextItem(str(actuator_id), self)

        self._set_default(point_size)

    def _set_default(self, point_size, width_pen=1):
        """Do the default settings.

        Parameters
        ----------
        point_size : `int`
            Point size of the text.
        width_pen : `int`, optional
            Width of the pen. (the default is 1)
        """

        font = self.label_id.font()
        font.setPointSize(point_size)
        self.label_id.setFont(font)

        pen = QPen(Qt.black)
        pen.setWidth(width_pen)
        self.setPen(pen)

        self.setBrush(Qt.red)

    def set_position_label_id(self, x, y):
        """Set the position of actuator ID label.

        Parameters
        ----------
        x : `float`
            Actuator ID label x position on the mirror's view.
        y : `float`
            Actuator ID label y position on the mirror's view.
        """
        self.label_id.setPos(x, y)

    def show_alias(self, is_alias):
        """Show the alias of actuator or not.

        Parameters
        ----------
        is_alias : `bool`
            Is the alias or not. If False, show the actuator ID.
        """

        if is_alias:
            self.label_id.setPlainText(self._alias)
        else:
            self.label_id.setPlainText(str(self._acutator_id))

    def update_magnitude(self, magnitude, magnitude_min, magnitude_max):
        """Update the magnitude. This will update the color of actuator on the
        mirror's view. If the magnitude is out of range, the limit of range
        will be used to show the color of magnitude on the view of mirror.

        Parameters
        ----------
        magnitude : `float`
            Magnitude.
        magnitude_min : `float`
            Minimal magnitude in gauge.
        magnitude_max : `float`
            Maximal magnitude in gauge.

        Raises
        ------
        `ValueError`
            If minimum magnitude >= maximum magnitude.
        """

        if magnitude_min >= magnitude_max:
            raise ValueError("Minimum magnitude should be less than maximum magnitude.")

        self._magnitude = magnitude

        # If the magnitude is out of range, use the limit of range instead
        # to decide the color to show
        if magnitude > magnitude_max:
            magnitude_color = magnitude_max
        elif magnitude < magnitude_min:
            magnitude_color = magnitude_min
        else:
            magnitude_color = magnitude

        magnitude_ratio = (magnitude_color - magnitude_min) / (
            magnitude_max - magnitude_min
        )

        self.setBrush(Gauge.get_color(magnitude_ratio))
