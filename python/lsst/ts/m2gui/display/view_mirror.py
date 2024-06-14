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

__all__ = ["ViewMirror"]

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsView
from qasync import asyncSlot

from .item_actuator import ItemActuator


class ViewMirror(QGraphicsView):
    """View on the mirror populated by actuators.

    Attributes
    ----------
    actuators : `list` [`ItemActuator`]
        Items of the actuator.
    mirror_radius : `float` or `int`
        Radius of the mirror in meter.
    """

    SIZE_SCENE = 500

    # Diameter of the actuator on the scene
    DIAMETER = 34

    def __init__(self) -> None:
        self._mirror = self._create_mirror()
        super().__init__(self._mirror)

        self.actuators: list[ItemActuator] = list()

        self.mirror_radius = 1

    def _create_mirror(self, point_size: int = 8) -> QGraphicsScene:
        """Create the mirror scene.

        Parameters
        ----------
        point_size : `int`, optional
            Point size of the text. (the default is 8)

        Returns
        -------
        mirror : `PySide6.QtWidgets.QGraphicsScene`
            Mirror scene.
        """

        # Create the mirror
        mirror = QGraphicsScene(0, 0, self.SIZE_SCENE, self.SIZE_SCENE)
        mirror.selectionChanged.connect(self._show_selected_actuator_force)

        # Add the text item to mirror
        font = QFont()
        font.setPointSize(point_size)

        text_force = mirror.addText("Actuator Force:\nID: -1, force: 0.00 N", font)
        text_force.setVisible(False)

        return mirror

    @asyncSlot()
    async def _show_selected_actuator_force(self) -> None:
        """Show the selected actuator force."""

        selected_actuator = self.get_selected_actuator()

        text_force = self.get_text_force()
        if text_force is not None:
            text_force.setVisible(selected_actuator is not None)

    def get_selected_actuator(self) -> ItemActuator | None:
        """Get the selected actuator.

        Returns
        -------
        `ItemActuator` or None
            Selected actuator. None if there is no selection.
        """

        selected_items = self._mirror.selectedItems()
        if len(selected_items) != 0:
            return selected_items[0]
        else:
            return None

    def get_text_force(self) -> QGraphicsTextItem | None:
        """Get the text item of actuator force.

        Returns
        -------
        `PySide6.QtWidgets.QGraphicsTextItem` or None
            Text item of the force actuator.
        """

        for item in self.items():
            if isinstance(item, QGraphicsTextItem):
                if item.toPlainText().startswith("Actuator Force:"):
                    return item

        return None

    def add_item_actuator(
        self, actuator_id: int, alias: str, x: float, y: float, point_size: int = 8
    ) -> None:
        """Add the actuator item.

        Parameters
        ----------
        actuator_id : `int`
            Actuator ID.
        alias : `str`
            Alias of the actuator.
        x : `float`
            Actuator x position in meter.
        y : `float`
            Actuator y position in meter.
        point_size : `int`, optional
            Point size of the text. (the default is 8)
        """

        # Calculate the position of actuator on the mirror's view
        center = self.SIZE_SCENE // 2
        magnification = self._calculate_magnification()

        # The offset of center is to consider the origin of ItemActuator as a
        # child of QGraphicsEllipseItem
        offset_center = self.DIAMETER // 2
        pos_x = center + int(x * magnification) - offset_center
        pos_y = center + int(y * magnification) - offset_center

        actuator = ItemActuator(
            pos_x, pos_y, self.DIAMETER, actuator_id, alias, point_size
        )

        # Set the label of actuator ID
        offset = self.DIAMETER // 2 - point_size
        actuator.set_position_label_id(pos_x + offset, pos_y)

        self.actuators.append(actuator)

        self._mirror.addItem(actuator)

    def _calculate_magnification(self, margin: int = 10) -> int:
        """Calculate the magnification. This is to re-dimensition the physical
        position of actuator to the graphical scene.

        Parameters
        ----------
        margin : `int`, optional
            Margin. (the default is 10)

        Returns
        -------
        `int`
            Magnification.
        """
        return (
            self.SIZE_SCENE // 2 - self.DIAMETER // 2 - margin
        ) // self.mirror_radius

    def show_alias(self, is_alias: bool) -> None:
        """Show the alias of actuator or not.

        Parameters
        ----------
        is_alias : `bool`
            Is the alias or not. If False, show the actuator ID.
        """

        for actuator in self.actuators:
            actuator.show_alias(is_alias)
