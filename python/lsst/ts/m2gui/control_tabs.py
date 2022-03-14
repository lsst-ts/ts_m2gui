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

__all__ = ["ControlTabs"]

from PySide2 import QtCore
from PySide2.QtWidgets import QListWidgetItem, QListWidget


class ControlTabs(object):
    """Control tables.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.
    list_widget : `PySide2.QtWidgets.QListWidget`
        List widget that has the control tables.

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    """

    def __init__(self, log):
        self.log = log

        self.list_widget = QListWidget()

        self._setup_list_widget()

    def _setup_list_widget(self):
        """Setup the list widget."""
        self._create_item("Overview")
        self._create_item("Actuator Control")
        self._create_item("Configuration View")
        self._create_item("Cell Status")
        self._create_item("Utility View")
        self._create_item("Rigid Body Position")
        self._create_item("Detailed Force")
        self._create_item("Diagnostics")
        self._create_item("Alarms/Warnings")

    def _create_item(self, name):
        """Create a standard list widget item, for option panel.

        Parameters
        ----------
        name : `str`
            Name of the option button

        Returns
        -------
        item : `PySide2.QtWidgets.QListWidgetItem`
            Created option button
        """
        item = QListWidgetItem(self.list_widget)
        item.setText(name)
        item.setTextAlignment(QtCore.Qt.AlignLeft)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        return item

    def get_tab(self, name):
        """Get the table.

        Parameters
        ----------
        name : `str`
            Name of the Table.

        Returns
        -------
        `PySide2.QtWidgets.QListWidgetItem` or None
            Table object. None if nothing.
        """
        count = self.list_widget.count()
        for idx in range(0, count):
            item = self.list_widget.item(idx)
            if item.text() == name.strip():
                return item

        return None
