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

from PySide2.QtWidgets import QListWidget
from PySide2.QtCore import Qt


class ControlTabs(QListWidget):
    """Control tables.

    Parameters
    ----------
    log : `logging.Logger`
        A logger.

    Attributes
    ----------
    log : `logging.Logger`
        A logger.
    """

    def __init__(self, log):
        super().__init__()

        self.log = log

        self._setup_list_widget()

    def _setup_list_widget(self):
        """Setup the list widget."""

        # self.addItem() is from the upstream
        self.addItem("Overview")
        self.addItem("Actuator Control")
        self.addItem("Configuration View")
        self.addItem("Cell Status")
        self.addItem("Utility View")
        self.addItem("Rigid Body Position")
        self.addItem("Detailed Force")
        self.addItem("Diagnostics")
        self.addItem("Alarms/Warnings")

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

        # self.findItems() is from the upstream
        try:
            return self.findItems(name, Qt.MatchExactly)[0]
        except IndexError:
            return None
