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

__all__ = ["TabDefault"]

from PySide2.QtWidgets import QDockWidget, QWidget, QScrollArea


class TabDefault(QDockWidget):
    """Default table.

    Parameters
    ----------
    title : `str`
        Table's title.
    model : `Model`
        Model class.

    Attributes
    ----------
    model : `Model`
        Model class.
    """

    def __init__(self, title, model):
        super().__init__()
        self.setWindowTitle(title)

        self.setWidget(QWidget())

        self.model = model

    def set_widget_scrollable(self, widget, is_resizable=False):
        """Set the widget to be scrollable.

        Parameters
        ----------
        widget : `PySide2.QtWidgets.QWidget`
            Widget.
        is_resizable : `bool`, optional
            Is resizable or not. (the default is False)

        Returns
        -------
        scroll_area : `PySide2.QtWidgets.QScrollArea`
            Scrollable area.
        """

        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(is_resizable)

        return scroll_area
